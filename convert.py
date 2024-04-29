import os
import sys
import click
import glob
import logging
import chardet
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


@click.command()
@click.option("--path", prompt="The path", help="Location of files")
@click.option("--prefix", prompt="The file prefix pattern", help="File prefix pattern")
@click.option("--skip", default=2, help="Number header lines to skip")
def main(path, prefix, skip):
    m = []
    s = []
    # Iterate over all files
    for filename in glob.glob(f"{os.path.join(path, prefix)}*"):
        # Get size of file
        file_stats = os.stat(filename)
        # Guess encoding of file
        with open(filename, "rb") as f:
            result = chardet.detect(f.read(max(int(file_stats.st_size / 100), 1)))
        logger.info(
            f"Reading data from {filename}, {file_stats.st_size / 1024} kb with encoding {result['encoding']}"
        )
        # Read file into datafram
        df = pd.read_csv(
            filename,
            header=[0, 1],  # Use both header lines
            encoding=result["encoding"],
            delimiter="\t",
            dtype=float,
            skiprows=2,  # Skip first 2 lines
            parse_dates=[0, 1],  # Combine Datum and Zeit
            date_format="%d-%m-%Y %H:%M:%S.%f",
            na_values={"?"},
        )
        # Calc mean() and store result
        m.append(df.mean(numeric_only=True))
        # Calc std() and store result
        s.append(df.std(numeric_only=True))

    # Merge mean() results
    mdf = pd.concat(m, axis=1)
    mdf.to_excel("mean.xlsx")
    mdf.plot()
    plt.savefig("mean.pdf")
    logger.info("Created mean.xlsx")
    # Merge sdt() results
    sdf = pd.concat(s, axis=1)
    sdf.to_excel("std.xlsx")
    sdf.plot()
    plt.savefig("std.pdf")
    logger.info("Created std.xlsx")


if __name__ == "__main__":
    main()
