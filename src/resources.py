import json
import os
import re
from dataclasses import dataclass
from textwrap import dedent
from typing import Mapping, Optional, Any

from arn import Arn

# These technically might have ARNs, but are never referred to as such in the API.
FAKE_ARNS = {
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazonec2.html#amazonec2-resources-for-iam-policies
    r'i-[a-z0-9]+': 'arn:aws:ec2:::instance/',
}


@dataclass
class ResourceName:
    template: str
    mappings: Mapping[str, str]


@dataclass
class ResourceLink:
    templateUri: str
    mappings: Mapping[str, str]


@dataclass
class ResourceType:
    type: str
    resourceName: ResourceName
    cfnType: Optional[str] = None
    startsWith: Optional[str] = None
    regex: Optional[str] = None
    resourceLink: Optional[ResourceLink] = None

    @classmethod
    def from_arn(cls, arn: str) -> 'ResourceType':
        # Exceptions
        arn = to_arn(arn)
        with open(os.path.join(os.path.dirname(__file__), 'data', f'{arn.service}.json'), 'r') as fh:
            resource_types = json.load(fh)

        for resource_type in resource_types:
            resource_type = cls._to_class(resource_type)
            if resource_type.matches(arn):
                return resource_type

        raise Exception(f"resource not found for {arn.input_arn} in {arn.service}")

    def matches(self, arn: Arn) -> bool:
        return self._get_match(arn) is not None

    def resource_name_for_arn(self, arn: Arn) -> str:
        return self._replace(self.resourceName.template, self.resourceName.mappings, arn, self._get_match(arn))

    def resource_link_for_arn(self, arn: Arn) -> Optional[str]:
        if self.resourceLink is None:
            return None

        console_url = "https://console.${awsPartition}.amazon.com"
        return self._replace(console_url + self.resourceLink.templateUri, self.resourceLink.mappings, arn,
                             self._get_match(arn))

    def _get_match(self, arn: Arn) -> Optional[Mapping[str, str]]:
        if self.startsWith is not None:
            if arn.rest.startswith(self.startsWith):
                return {"_rest_": arn.rest[len(self.startsWith):]}
        if self.regex is not None:
            if match := re.match(self.regex, arn.rest, flags=re.IGNORECASE):
                return match.groupdict()

        return None

    @staticmethod
    def _replace(template: str, mapping: Mapping[str, str], arn: Arn, match: Mapping[str, str]) -> str:
        for k, v in mapping.items():
            template = template.replace(f"${{{k}}}", match[v])
        template = template.replace("${awsPartition}", arn.partition)
        template = template.replace("${awsRegion}", arn.region)
        template = template.replace("${awsAccountId}", arn.account)
        return template

    @classmethod
    def _to_class(cls, resource_dict: Mapping[str, Any]) -> 'ResourceType':
        input_dict = {k: v for k, v in resource_dict.items() if not k.startswith('_')}
        output = cls(**input_dict)
        output.resourceName = ResourceName(**input_dict['resourceName'])
        output.resourceLink = ResourceLink(**input_dict['resourceLink']) if input_dict.get('resourceLink') else None
        return output


@dataclass
class Resource:
    arn: Arn
    resource_type: ResourceType

    @property
    def type(self) -> str:
        return self.resource_type.type

    @property
    def name(self) -> str:
        return self.resource_type.resource_name_for_arn(self.arn)

    @property
    def cloudformation_type(self) -> Optional[str]:
        return self.resource_type.cfnType

    @property
    def console_link(self) -> Optional[str]:
        return self.resource_type.resource_link_for_arn(self.arn)

    @property
    def partition(self) -> str:
        return self.arn.partition

    @property
    def service(self) -> str:
        return self.arn.service

    @property
    def region(self) -> str:
        return self.arn.region

    @property
    def account(self) -> str:
        return self.arn.account

    @classmethod
    def from_arn(cls, arn: str) -> 'Resource':
        resource_type = ResourceType.from_arn(arn)
        return cls(to_arn(arn), resource_type)

    def to_text(self):
        output = dedent(f"""
            Partition:       {self.partition}
            Service:         {self.service}
            Region:          {self.region}
            Account:         {self.account}
            Type:            {self.type}
            Name:            {self.name}
            """).strip()
        if self.cloudformation_type is not None:
            output += f"\nCloudFormation:  {self.cloudformation_type}"
        if self.console_link is not None:
            output += f"\nConsole:         {self.console_link}"

        return output


def to_arn(arn: str) -> Arn:
    for pattern, prefix in FAKE_ARNS.items():
        if re.match(pattern, arn, re.IGNORECASE):
            arn = prefix + arn

    return Arn(arn)
