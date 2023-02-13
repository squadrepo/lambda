This is where we can write shared code for our Lambda functions.  

After making updates, zip the *contents* of this 'layer' directory -- including the 'python' directory, which is where our custom code goes, but excluding this readme -- and upload it in the AWS console as a new version of the commonLayer layer.  Keep in mind, you will need to manually add this new version of the layer to every Lambda function that you want to use it.  

Here is an article that goes through the basic process: https://unbiased-coder.com/create-python-lambda-layer/

If we need to use any Python packages/libraries outside of the standard library in one of our Lambda functions, we would install them through this layer as well, but additional work is required. We need to upload the Linux versions of these packages since that is what AWS uses.  This article goes into detail: https://aws.plainenglish.io/creating-aws-lambda-layer-for-python-runtime-1d1bc6c5148d

The layer contains a test function that helloWorld prints to the console.