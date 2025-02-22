#!/usr/bin/env python3

from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO
from os import getenv, makedirs, path
from sys import exit

from copr.v3 import Client

basicConfig(
    level=getenv('COPR_BUILD_LOG', INFO)
)
logger = getLogger(__name__)

def main():
    copr_api_token_cfg = getenv('COPR_API_TOKEN_CONFIG')
    copr_cfg_path = path.expanduser("~/.config/copr")
    copr_cfg_dir = path.dirname(copr_cfg_path)
    logger.info(f"copr configuration path: {copr_cfg_path}")

    if copr_api_token_cfg is None and not path.exists(copr_cfg_path):
        logger.error("you need to pass the COPR API configuration as COPR_API_TOKEN_CONFIG")
        exit(1)

    if not path.isdir(copr_cfg_dir):
        logger.info(f"creating {copr_cfg_path}")
        makedirs(copr_cfg_dir)

    if not path.exists(copr_cfg_path):
        with open(copr_cfg_path, "w") as copr_cfg_file:
            logger.info(f"writing credentials to {copr_cfg_path}")
            print(copr_api_token_cfg, file=copr_cfg_file)
    else:
        logger.info("detected existing config, avoiding overwrite")

    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--project-name",
        required=True,
        help="COPR Project Name",
    )
    arg_parser.add_argument(
        "--package-name",
        required=True,
        help="COPR Package Name",
    )
    arg_parser.add_argument(
        "--owner",
        required=True,
        help="COPR Project Owner",
    )
    arg_parser.add_argument(
        "--git-remote",
        required=True,
        help="Source Control Remote"
    )
    arg_parser.add_argument(
        "--committish",
        default="main",
        help="Git Committish to build in COPR",
    )
    arg_parser.add_argument(
        "--source-build-method",
        default="rpkg",
        help="COPR Source Build Method for this package (https://docs.pagure.org/copr.copr/user_documentation.html#scm)",
    )

    cli_args = arg_parser.parse_args()
    logger.info(f"copr-build: {cli_args}")

    copr_client = Client.create_from_config_file()
    try:
        copr_package = copr_client.package_proxy.get(
            cli_args.owner,
            cli_args.project_name,
            cli_args.package_name,
        )
    except:
        try:
            logger.warning("package not found, creating package")
            copr_package = copr_client.package_proxy.add(
                cli_args.owner,
                cli_args.project_name,
                cli_args.package_name,
                "scm",
                {
                    "clone_url": cli_args.git_remote,
                    "scm_type": "git",
                    "comittish": cli_args.committish,
                    "source_build_method": cli_args.source_build_method,
                }
            )
            logger.info(f"created package {copr_package}")
        except Exception as e:
            logger.error("could not create package")
            logger.error(e)
            exit(1)


    try:
        copr_client.package_proxy.build(
            cli_args.owner,
            cli_args.project_name,
            cli_args.package_name,
        )
        logger.info(f"triggered copr build for {cli_args.owner}/{cli_args.project_name}/{cli_args.package_name}")
    except Exception as e:
        logger.error("could not trigger build")
        logger.error(e)
        exit(1)


if __name__ == "__main__":
    main()
