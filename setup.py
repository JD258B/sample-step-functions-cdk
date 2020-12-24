import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="sample_step_functions_cdk",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "sample_step_functions_cdk"},
    packages=setuptools.find_packages(where="sample_step_functions_cdk"),

    install_requires=[
        "aws-cdk.core==1.77.0",
        "aws_solutions_constructs.aws_events_rule_step_function",
        "aws-cdk.aws-events",
        "aws-cdk.aws-stepfunctions",
        "aws-cdk.aws-stepfunctions-tasks",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-sns",
        "aws-cdk.aws-sns-subscriptions",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-apigateway",
        "aws-cdk.aws-lambda-event-sources"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
