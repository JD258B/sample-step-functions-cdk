from aws_cdk import (
    core,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_events as events,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_source,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_apigateway as apigw,
    aws_iam as iam
)

from aws_solutions_constructs.aws_events_rule_step_function import EventsRuleToStepFunction, EventsRuleToStepFunctionProps

class SampleStepFunctionsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        iam_restricted_actions = 's3:DeleteBucket,s3:DeleteObject'

        # SNS Topic and Subscription
        policy_alert_topic = sns.Topic(self, 'policy-alert-topic', display_name='policy-alert-topic', topic_name='policy-alert-topic')

        policy_alert_topic.add_subscription(subs.EmailSubscription(email_address=''))

        # Lambda Function for receiving user input

        receive_user_api_function = _lambda.Function(
            self, 'receive-user-api-function',
            handler='app.handler',
            code=_lambda.AssetCode('recieveUser'),
            runtime=_lambda.Runtime.NODEJS_10_X,
            function_name='validate-iam-policies-receive-user-choice',
            initial_policy=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=['states:SendTaskSuccess'],
                    resources=['*']
                )
            ]
        )

        # API Gateway integration for receive user 

        receive_user_api = apigw.RestApi(self, "receive-user-rest-api", rest_api_name="receive-user-rest-api")

        allow_api_resource = receive_user_api.root.add_resource('allow')
        deny_api_resource = receive_user_api.root.add_resource('deny')

        receive_user_api_integration = apigw.LambdaIntegration(receive_user_api_function,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        allow_api_resource.add_method("GET", receive_user_api_integration)
        deny_api_resource.add_method("GET", receive_user_api_integration)

        # Function to validate the policy

        validate_policy = _lambda.Function(
            self, 'validate-policy-function',
            handler='app.handler',
            code=_lambda.AssetCode('validatePolicy'),
            runtime=_lambda.Runtime.NODEJS_10_X,
            function_name='validate-iam-policies-validate-policy',
            environment={
                'restrictedActions': iam_restricted_actions
            }
        )

        policy_changer_approve = _lambda.Function(
            self, 'policy-changer-approve-function',
            handler='app.handler',
            code=_lambda.AssetCode('policyChangerApprove'),
            runtime=_lambda.Runtime.NODEJS_10_X,
            function_name='validate-iam-policies-policy-changer-approve',
            environment={
                'restrictedActions': iam_restricted_actions
            },
            initial_policy=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=['iam:CreatePolicyVersion'],
                    resources=['*']
                )
            ]
        )

        revert_policy = _lambda.Function(
            self, 'revert-policy-function',
            handler='app.handler',
            code=_lambda.AssetCode('revertPolicy'),
            runtime=_lambda.Runtime.NODEJS_10_X,
            function_name='validate-iam-policies-revert-policy',
            environment={
                'restrictedActions': iam_restricted_actions
            },
            initial_policy=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=['iam:CreatePolicyVersion', 'iam:DeletePolicyVersion'],
                    resources=['*']
                )
            ]
        )

        ask_user = _lambda.Function(
            self, 'ask-user-function',
            handler='app.handler',
            code=_lambda.AssetCode('askUser'),
            runtime=_lambda.Runtime.NODEJS_10_X,
            function_name='validate-iam-policies-ask-user',
            environment={
                'restrictedActions': iam_restricted_actions,
                'Topic': policy_alert_topic.topic_arn,
                'APIAllowEndpoint': receive_user_api.url + 'allow',
                'APIDenyEndpoint': receive_user_api.url + 'deny'
            },
            initial_policy=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=['sns:Publish'],
                    resources=[policy_alert_topic.topic_arn]
                )
            ]
        )

        #Step Function defintion
        # IDs are set for how I wanted them to show up in Step Functions console

        modify_data_activity = sfn.Pass(
            self, 'ModifyData',
            result_path='$',
            parameters={
                'policy.$': '$.detail.requestParameters.policyDocument',
                'accountId.$': '$.detail.userIdentity.accountId',
                'region.$': '$.region',
                'policyMeta.$': '$.detail.responseElements.policy'
            }
        )

        validate_policy_task = sfn_tasks.LambdaInvoke(
            self, 'ValidatePolicy',
            lambda_function=validate_policy,
            payload=sfn.TaskInput.from_data_at('$'),
            result_path='$.taskresult'
        )

        allow_with_notification_task = sfn_tasks.SnsPublish(
            self, 'AllowWithNotification',
            input_path='$',
            message=sfn.TaskInput.from_data_at('$.taskresult.Payload.message'),
            topic=policy_alert_topic,
            subject='Policy change detected!'
        )

        choose_action = sfn.Choice(
            self, 'ChooseAction'
        )

        user_choice_action = sfn.Choice(
            self, 'UsersChoice'
        )

        ask_user_task = sfn_tasks.LambdaInvoke(
            self, 'AskUser',
            lambda_function=ask_user,
            result_path='$.taskresult',
            integration_pattern=sfn.IntegrationPattern('WAIT_FOR_TASK_TOKEN'),
            payload=sfn.TaskInput.from_object({
                'token': sfn.JsonPath.task_token})
        )

        approved_task = sfn_tasks.LambdaInvoke(
            self, 'Approved',
            lambda_function=policy_changer_approve,
            result_path='$.taskresult'
        )

        temp_remove_task = sfn_tasks.LambdaInvoke(
            self, 'TempRemove',
            lambda_function=revert_policy,
            payload=sfn.TaskInput.from_data_at('$'),
            result_path='$.taskresult'
        )

        denied_task = sfn.Pass(
            self, 'Denied'
        )

        sf_definition = modify_data_activity.next(validate_policy_task).next(
            choose_action.when(sfn.Condition.string_equals('$.taskresult.Payload.action', 'remedy'), temp_remove_task.next(
                ask_user_task).next(user_choice_action.when(sfn.Condition.string_equals('$.taskresult.action', 'delete'), denied_task).otherwise(
                    approved_task).afterwards())).otherwise(allow_with_notification_task).afterwards())
        
        # Solution Construct config

        event_rule_props = events.RuleProps(
            rule_name='validate-iam-policies-rule',
            event_pattern=events.EventPattern(
                source=['aws.iam'],
                detail_type=['AWS API Call via CloudTrail'],
                detail={
                    'eventSource': ['iam.amazonaws.com'],
                    'eventName': ['CreatePolicy']
                }
            )
        )        

        sf_state_machine_props = sfn.StateMachineProps(
            definition=sf_definition,
            state_machine_name='validate-iam-policies'
        )

        test = EventsRuleToStepFunction(self, 'test-events-rule-step-function-stack', event_rule_props=event_rule_props, state_machine_props=sf_state_machine_props)
