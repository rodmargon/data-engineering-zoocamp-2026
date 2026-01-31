#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import click
from sqlalchemy import create_engine
from tqdm.auto import tqdm


dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64"    
    }

parse_dates = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime"
    ]


def ingest_data(
        url: str,
        target_table: str,
        engine,
        chunk_size: int = 100000,
) -> pd.DataFrame:
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunk_size
    )

    first_chunk = next(df_iter)

    first_chunk.head(0).to_sql(name=target_table, con=engine, if_exists='replace')

    print(f"Table {target_table} created")

    first_chunk.to_sql(
        name=target_table ,
        con=engine,
        if_exists="append"
    )


    print(f"Inserted first chunk: {len(first_chunk)}")

    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )
        print(f"Inserted chunk: {len(df_chunk)}")

    print(f'done ingesting to {target_table}')


@click.command()
@click.option('--year', default=2021, help='Year of the data')
@click.option('--month', default=1, help='Month of the data')
@click.option('--target_table', default='yellow_taxi_data', help='Target table name')
@click.option('--pg_user', default='root', help='Postgres user')
@click.option('--pg_password', default='root', help='Postgres password')
@click.option('--pg_host', default='localhost', help='Postgres host')
@click.option('--pg_port', default='5432', help='Postgres port')
@click.option('--pg_db', default='ny_taxi', help='Postgres database')
@click.option('--chunk_size', default=100000, help='Chunk size')
def main(year, month, target_table, pg_user, pg_password, pg_host, pg_port, pg_db, chunk_size):
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'


    ingest_data(
        url=url,
        engine=engine,
        target_table=target_table,
        chunk_size=chunk_size
    )



if __name__ == '__main__':
    main()
