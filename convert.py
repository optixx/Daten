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
@click.option("--skip-header", default=2, help="Number header lines to skip")
@click.option("--write-excel", default=True, help="Write results to excel files")
@click.option("--write-pdf", default=False, help="Plot results to pdf file")
def main(path, prefix, skip_header, write_excel, write_pdf):
    results_mean = []
    results_std = []
    output_dir = os.path.abspath(path)  # Get absolute path for output directory
    logger.info(f"Output directory: {output_dir}")  # Output the output directory path
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
        # Read file into dataframe
        df = pd.read_csv(
            filename,
            header=[0, 1],  # Use both header lines
            encoding=result["encoding"],
            delimiter="\t",
            dtype=float,
            skiprows=skip_header,  # Skip first 2 lines
            parse_dates=[0, 1],  # Combine Datum and Zeit
            date_format="%d-%m-%Y %H:%M:%S.%f",
            na_values={"?"},
        )
        # Calculate mean and store result
        mean_values = df.mean(numeric_only=True)
        # Add calculated columns
        # N
        # M
        # PWG
        # Drosselklappe
        # NW_Einlass
        # m_HFM
        # R_EN.HFM5_Extern
        # m_C_cor_C_2
        # CONSUMPTION
        # Kraftstoffdruck
        # P_Amb
        # T_Amb
        # Phi_Amb
        # lambda_C
        # P_Air_Int
        # P_Exh_O
        # P_TC_1
        # T_TC_1_1
        # T_TC_1_2
        # P_TC_2
        # T_TC_2_1
        # T_TC_2_2
        # P_TC_3
        # P_TC_4
        # p_tot_TC_1_C
        # p_tot_TC_2_C
        # p2t/p1t_C
        # T_Air_Int
        # T_CAC_1
        # T_CAC_2
        # T_Cool_Eng
        # T_Oil_Eng
        # T_TC_1
        # T_TC_IN_LE
        # T_TC_2
        # T_TC_1_05
        # P_TC_IN_LE
        # P_TC_IN_LE_A
        # T_TC_3
        # T_TC_4
        # T_tot_TC_1_C
        # T_tot_TC_2_C
        # N_Turbo
        # N_C_cor_C
        # u_red
        # V_Vehicle
        s = pd.Series(
            df["P_TC_IN_LE"].values[0] / df["P_TC_1"].values[0],
            index=[("Q_P_LE/P1", "bar")],
        )
        mean_values = pd.concat([mean_values, s])

        # Subtraction Leading Edge - Eingangstemperatur
        # mean_values["T_LE-T_1_2"] = df["T_TC_IN_LE"] - df["T_TC_1_2"]
        # Subtraction T2 (Temperatur nach Verdichter) - Temperatur Leading Edge
        # mean_values["T2-T_LE"] = df["T_TC_2"] - df["T_TC_IN_LE"]
        # Subtraction of two columns
        # mean_values["T2-T_1_2"] = df["T_TC_2"] - df["T_TC_1_2"]
        with pd.option_context(
            "display.max_rows", None, "display.max_columns", None
        ):  # more options can be specified also
            print(mean_values)
        results_mean.append(mean_values)
        # Calc std() and store result
        results_std.append(df.std(numeric_only=True))

    # Merge mean() results
    mdf = pd.concat(results_mean, axis=1)
    print(mdf.columns)
    # Subtract values from "P_TC_2" channel from "P_TC_1" channel and store the result in a new column
    mdf["P_TC_2_minus_P_TC_1"] = mdf["P_TC_1"] - mdf["P_TC_2"]
    if write_excel:
        mdf.to_excel(os.path.join(output_dir, "mean.xlsx"))
        logger.info(f"Created mean.xlsx in {output_dir}")
    if write_pdf:
        mdf.plot()
        plt.savefig(os.path.join(output_dir, "mean.pdf"))
        plt.close()
        logger.info(f"Created mean.pdf in {output_dir}")
    # Merge std() results
    sdf = pd.concat(results_std, axis=1)
    if write_excel:
        sdf.to_excel(os.path.join(output_dir, "std.xlsx"))
        logger.info(f"Created std.xlsx in {output_dir}")
    if write_pdf:
        sdf.plot()
        plt.savefig(os.path.join(output_dir, "std.pdf"))
        plt.close()
        logger.info(f"Created std.pdf in {output_dir}")

    # Merge std()and mean() results in one Excel File

    if write_excel:
        with pd.ExcelWriter(os.path.join(output_dir, "summary.xlsx")) as writer:
            # Modify index names of sdf DataFrame
            modified_index = [
                (f"{idx[0]}_s", idx[1]) if isinstance(idx, tuple) and i != 1 else idx
                for i, idx in enumerate(sdf.index)
            ]
            sdf.index = pd.MultiIndex.from_tuples(modified_index)

            # Concatenate mean and std DataFrames vertically
            combined_df = pd.concat([mdf, sdf])

            # Write combined DataFrame to Excel
            combined_df.to_excel(writer, sheet_name="Summary")

    logger.info(f"Created summary.xlsx in {output_dir}")


if __name__ == "__main__":
    main()
