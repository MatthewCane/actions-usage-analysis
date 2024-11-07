#!python3
import polars as pl
import streamlit as st


def main():
    st.write("# GitHub Actions Usage Report")
    st.write(
        """
        ---

        Analyses a GitHub Actions usage report to provide insights into the cost and usage of GitHub Actions.

        To get your personal usage report, go to your GitHub account and navigate to:

        > Settings > Billing and plans > Plans and usage > Get usage report

        To get an organisation usage report, go to your organisation and navigate to:

        > Settings > Billing and plans > Get usage report

        GitHub will email you when the report is ready. Once you have the report, upload it below.

        ---
        """
    )
    uploaded_file = st.file_uploader("Upload your usage report", type="csv")

    st.write("---")

    if uploaded_file is None:
        st.stop()

    pl.Config.set_tbl_hide_dataframe_shape(True)
    pl.Config.set_tbl_hide_column_data_types(True)
    df = pl.read_csv(uploaded_file)

    # Calculate the total price for each row
    df = df.with_columns(
        (pl.col("Quantity") * pl.col("Price Per Unit ($)")).alias("Total Cost ($)"),
    )

    # Convert the Date column to a Date type
    df = df.with_columns(pl.col("Date").cast(pl.Date))

    # Combine Repository Slug and Owner
    df = df.with_columns(
        (pl.col("Owner") + "/" + pl.col("Repository Slug")).alias("Repository Slug")
    )

    top_10_most_expensive_repositories_by_total_cost = (
        df.group_by("Repository Slug")
        .agg(pl.sum("Total Cost ($)").alias("Total Cost Per Repository ($)"))
        .sort("Total Cost Per Repository ($)", descending=True)
        .head(10)
        .with_columns(pl.col("Total Cost Per Repository ($)").round(2))
    )

    top_10_most_expensive_repository_products_by_total_cost = (
        df.group_by(("Product", "Repository Slug"))
        .agg(pl.sum("Total Cost ($)").alias("Total Cost Per Product ($)"))
        .sort("Total Cost Per Product ($)", descending=True)
        .head(10)
        .with_columns(pl.col("Total Cost Per Product ($)").round(2))
    )

    top_10_most_expensive_workflows_by_total_cost = (
        df.with_columns(pl.col("Actions Workflow").str.split("/").list.last())
        .group_by(("Actions Workflow", "Repository Slug"))
        .agg(pl.sum("Total Cost ($)").alias("Total Cost Per Workflow ($)"))
        .filter(pl.col("Actions Workflow") != "null")
        .sort("Total Cost Per Workflow ($)", descending=True)
        .head(10)
        .with_columns(pl.col("Total Cost Per Workflow ($)").round(2))
    )

    top_10_most_expensive_repositories_by_storage_cost = (
        df.filter(pl.col("Product") == "Shared Storage")
        .group_by(("Repository Slug"))
        .agg(pl.sum("Total Cost ($)").alias("Total Cost Per Repository ($)"))
        .sort("Total Cost Per Repository ($)", descending=True)
        .head(10)
        .with_columns(pl.col("Total Cost Per Repository ($)").round(2))
    )

    avg_cost_per_day = (
        df.group_by("Date")
        .agg(pl.sum("Total Cost ($)").alias("Average Cost Per Day ($)"))
        .mean()
        .select(pl.col("Average Cost Per Day ($)").round(2))
    )

    avg_cost_per_month = avg_cost_per_day.select(
        (pl.col("Average Cost Per Day ($)") * 30).alias("Estimated Cost Per Month ($)")
    ).with_columns(pl.col("Estimated Cost Per Month ($)").round(2))

    top_10_cost_by_user = (
        df.group_by("Username")
        .agg(pl.sum("Total Cost ($)").alias("Total Cost Per User ($)"))
        .sort("Total Cost Per User ($)", descending=True)
        .head(10)
        .with_columns(pl.col("Total Cost Per User ($)").round(2))
    )

    start_date = df["Date"].min()
    end_date = df["Date"].max()
    time_period = (end_date - start_date).days
    st.write(
        f"This report covers **{time_period} days** between **{start_date}** and **{end_date}**"
    )

    st.write("### Top 10 most expensive repositories by total cost")
    st.write(top_10_most_expensive_repositories_by_total_cost)
    st.write("### Top 10 most expensive repository products by total cost")
    st.write(top_10_most_expensive_repository_products_by_total_cost)
    st.write("### Top 10 most expensive workflows by total cost")
    st.write(top_10_most_expensive_workflows_by_total_cost)
    st.write("### Top 10 most expensive repositories by storage cost")
    st.write(top_10_most_expensive_repositories_by_storage_cost)
    st.write("### Average cost per day")
    st.write(avg_cost_per_day)
    st.write("### Estimated cost per month")
    st.write(avg_cost_per_month)
    st.write("### Top 10 users by cost")
    st.write(top_10_cost_by_user)


if __name__ == "__main__":
    main()
