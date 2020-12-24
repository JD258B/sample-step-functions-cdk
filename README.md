# AWS CDK Python Lab
---
## Automated security orchestrator with AWS Step Functions

Took the lab [Automated security orchestrator with AWS Step Functions](https://github.com/aws-samples/automating-a-secutity-incident-with-step-functions) and created it in the AWS CDK in Python.

I utilized the [aws-events-rule-step-function](https://docs.aws.amazon.com/solutions/latest/constructs/aws-events-rule-step-function.html) Solution Construct for the Eventbridge Rule and the Step Function.

I walked through recreating this as a way to help learn the AWS CDK.

For the API Gateway and Lambda integration on one of the Lambda Functions, I initially tried to create it with the Lambda event source construct but I was unable to find a way to get the API URL back to use in another Lambda Functions environment variables. I also tried using the aws-apigateway-lambda Solution Construct but ran into the same issue. 

As I deployed the State Machine I had to make changes to the payload and result path in a few spots.

The Ask User Lambda Function needed to be updated as well. It was not sending the API Gateway URLs correctly. I added the message from the event to show the IAM policy and additional information.

Here is the Application Architecture diagram from the aws-samples repo:
![Application Architecture](/img/architecture.png)

Here is the Step Function Workflow:
![Step Function Workflow](/img/Step-Functions-Management-Console.png)


---
# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
