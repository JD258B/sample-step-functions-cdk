#!/usr/bin/env python3

from aws_cdk import core

from sample_step_functions_cdk.sample_step_functions_cdk_stack import SampleStepFunctionsCdkStack


app = core.App()
SampleStepFunctionsCdkStack(app, "sample-step-functions-cdk")

app.synth()
