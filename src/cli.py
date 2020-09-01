import argparse

from .resources import Resource


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ARN to console link")
    parser.add_argument('arn')
    args = parser.parse_args()
    resource = Resource.from_arn(args.arn)
    print(resource.to_text())


if __name__ == '__main__':
    main()
