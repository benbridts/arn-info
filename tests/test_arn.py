import pytest

from resources import Resource

@pytest.mark.parametrize("arn, partition, service, region, account, type, name, cloudformation_type, console_link", [
    # CloudFormation
    (
        'arn:aws:cloudformation:eu-west-1:123456789012:changeSet/Name-Of-ChangeSet/ed6c6f7f-688f-4e2b-9cf3-0e6fd4fb4cda',
        'aws', 'cloudformation', 'eu-west-1', '123456789012', 'changeset', 'Name-Of-ChangeSet', None,
        None,
    ),
    (
        'arn:aws:cloudformation:eu-west-1:123456789012:stackset/stackset-name:49353e9c-4a73-435a-86c8-d5cfc9feadc9',
        'aws', 'cloudformation', 'eu-west-1', '123456789012', 'stackset', 'stackset-name', None,
        'https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacksets/stackset-name:49353e9c-4a73-435a-86c8-d5cfc9feadc9/info',
    ),
    (
        'arn:aws:cloudformation:eu-west-1:123456789012:stack/stack-name/b7671440-7e54-11ea-916a-0a6a2f25f2be',
        'aws', 'cloudformation', 'eu-west-1', '123456789012', 'stack', 'stack-name', 'AWS::CloudFormation::Stack',
        'https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/stackinfo?stackId=arn%3Aaws%3Acloudformation%3Aeu-west-1%3A123456789012%3Astack%2Fstack-name%2Fb7671440-7e54-11ea-916a-0a6a2f25f2be',
    ),
    # CodeCommit
    (
        'arn:aws:codecommit:eu-west-1:123456789012:repo_name',
        'aws', 'codecommit', 'eu-west-1', '123456789012', 'repository', 'repo_name', 'AWS::CodeCommit::Repository',
        'https://console.aws.amazon.com/codesuite/codecommit/repositories/repo_name/browse?region=eu-west-1'
    ),
    # EC2
    (
        'i-b9b4ffaa',
        'aws', 'ec2', '', '', 'instance', 'i-b9b4ffaa', 'AWS::EC2::Instance',
        'https://console.aws.amazon.com/ec2/v2/home#Instances:instanceId=i-b9b4ffaa'
    )
])
def test_arn(arn, partition, service, region, account, type, name, cloudformation_type, console_link):
    resource = Resource.from_arn(arn)
    assert resource.partition == partition
    assert resource.service == service
    assert resource.region == region
    assert resource.account == account
    assert resource.type == type
    assert resource.name == name
    assert resource.cloudformation_type == cloudformation_type
    assert resource.console_link == console_link
