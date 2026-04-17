import click
import sys
from .db import init_db
from .collectors.visit_seoul import VisitSeoulCollector
from .collectors.seoul_open_data import SeoulOpenDataCollector
from .pipelines.build_master import process_and_merge_to_master

@click.group()
def cli():
    """Seoul Stay Market Research CLI"""
    pass

@cli.command(name='init')
def init():
    """데이터베이스 및 테이블 초기화"""
    init_db()
    click.echo("Database initialized.")

@cli.command(name='collect_visit')
def collect_visit():
    """Visit Seoul 데이터 수집 및 마스터 반영"""
    click.echo("Starting Visit Seoul collection...")
    collector = VisitSeoulCollector()
    items = collector.run()
    if items:
        process_and_merge_to_master(items, "visit_seoul")
        click.echo(f"Successfully processed {len(items)} items.")
    else:
        click.echo("No data found.")

@cli.command(name='collect_seoul')
def collect_seoul():
    """서울시 인허가 데이터 수집 및 마스터 반영"""
    click.echo("Starting Seoul Open Data collection...")
    collector = SeoulOpenDataCollector()
    items = collector.run()
    if items:
        process_and_merge_to_master(items, "seoul_open_data")
        click.echo(f"Successfully processed {len(items)} items.")
    else:
        click.echo("No data found.")

if __name__ == "__main__":
    cli()
