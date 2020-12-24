#!/usr/bin/env python3

from aws_cdk import core

from sample_step_functions_cdk.sample_step_functions_cdk_stack import SampleStepFunctionsCdkStack


app = core.App()
sfn_stack = SampleStepFunctionsCdkStack(app, "sample-step-functions-cdk")
core.Tags.of(sfn_stack).add('env', 'prod')
core.Tags.of(sfn_stack).add('service', 'validate-iam-policy')

app.synth()
