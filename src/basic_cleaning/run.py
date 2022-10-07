#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    """
    Function to download artifact, clean data and upload artifact to Weights & Biases
    """
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)
    # Download input artifact.
    logger.info("Downloading artifact")
    artifact_path = run.use_artifact(args.input_artifact).file()
    # Read and clean CSV file
    logger.info("Reading and cleaning CSV file")
    data_frame = pd.read_csv(artifact_path)
    # Drop outliers based on price
    idx = data_frame['price'].between(args.min_price, args.max_price)
    data_frame = data_frame[idx].copy()
    # Convert last_review to datetime
    data_frame['last_review'] = pd.to_datetime(data_frame['last_review'])
    idx = data_frame['longitude'].between(-74.25, -73.50) & data_frame['latitude'].between(40.5, 41.2)
    data_frame = data_frame[idx].copy()
    data_frame.to_csv("clean_sample.csv", index=False)
    logger.info(f"Uploading {args.output_artifact} to Weights & Biases")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="The input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price to consider",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price to consider",
        required=True
    )

    args = parser.parse_args()

    go(args)
