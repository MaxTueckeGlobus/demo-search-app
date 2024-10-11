from search import SearchApp

from globus_sdk.services.search.errors import SearchAPIError

import os
import pathlib
import json
import click

"""
{
  "@datatype": "GSearchIndex",
  "@version": "2017-09-01",
  "display_name": "test-search-index",
  "description": "maxs test search index",
  "id": "e32c842e-df0d-42cb-9844-6af771505357",
  "max_size_in_mb": 1,
  "size_in_mb": 0,
  "num_subjects": 0,
  "num_entries": 0,
  "creation_date": "2024-10-08 21:48:07",
  "subscription_id": null,
  "is_trial": true,
  "status": "open"
}
"""


@click.group()
def cli():
    pass


@cli.command()
def whoami():
	search_app = SearchApp()
	user_info = search_app.whoami()

	username = user_info.get("preferred_username", None)
	name = user_info.get("name", None)
	email = user_info.get("email", None)

	click.echo(f"Username: {username}")
	click.echo(f"Name: {name}")
	click.echo(f"Email: {email}")


@cli.command()
def logout():
	click.echo(f"Logging out")

	search_app = SearchApp()
	search_app.logout()


@cli.command()
@click.argument('display_name')
@click.argument('description')
def create_index(display_name, description):
	click.echo(f"Creating new search index: {display_name}")

	search_app = SearchApp()
	search_app.login()

	try:
		response = search_app.create_index(display_name, description)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)


@cli.command()
@click.argument('index_id')
def delete_index(index_id):
	click.echo(f"Deleting search index: {index_id}")

	search_app = SearchApp()
	search_app.login()

	try:
		response = search_app.delete_index(index_id)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)


@cli.command()
@click.argument('index_id')
@click.argument('subject')
@click.argument('data_path')
@click.option('--is-dir', default=False)
def ingest(index_id, subject, data_path, is_dir):
	search_app = SearchApp()
	search_app.login()

	if is_dir:
		count = 0
		for filename in os.listdir(data_path):
			file_path = os.path.join(data_path, filename)
			if pathlib.Path(file_path).suffix != ".json":
				click.echo(f"Skipping non json file: {file_path}")
				continue

			click.echo(f"Ingesting file {file_path} to search index {index_id}")

			with open(file_path) as f:
				data = json.load(f)
			_ingest_json(search_app, index_id, f"{subject}-{count}", data)
			count += 1
	else:
		if pathlib.Path(file_path).suffix != ".json":
			click.echo(f"Unable to ingest non json file: {data_path}")
			return

		click.echo(f"Ingesting file {data_path} to search index {index_id}")

		with open(data_path) as f:
			data = json.load(f)
		_ingest_json(search_app, index_id, subject, data)


@cli.command()
@click.argument('index_id')
@click.argument('query_path')
@click.option('--offset', default=0)
@click.option('--limit', default=10)
def search(index_id, query_path, offset, limit, ):
	search_app = SearchApp()
	search_app.login()

	with open(query_path) as f:
		query = json.load(f)

	click.echo(f"Running search query:\n {query} \non search index: {index_id}")

	try:
		response = search_app.search(index_id, query, offset=offset, limit=limit)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)


@cli.command()
@click.argument('index_id')
@click.argument('subject')
def search_entry(index_id, subject):
	click.echo(f"Searching for entry: {subject} on search index: {index_id}")

	search_app = SearchApp()
	search_app.login()

	try:
		response = search_app.get_search_entry(index_id, subject)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)


@cli.command()
@click.argument('index_id')
@click.argument('subject')
def delete_entry(index_id, subject):
	click.echo(f"Deleting entry: {subject} from search index: {index_id}")

	search_app = SearchApp()
	search_app.login()

	try:
		response = search_app.delete_search_entry(index_id, subject)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)


def _ingest_json(search_app, index_id, subject, data):
	try:
		response = search_app.ingest_json_data(index_id, subject, data)
		click.echo(response)
	except SearchAPIError as e:
		_format_error(e)
		

def _format_error(e):
	click.echo(f"Error ({e.http_status}): {e.messages}")
	if e.error_data is not None:
		click.echo(f"Cause: {e.error_data.get('cause', 'Unknown')}")
		click.echo(f"Recommended resolution: {e.error_data.get('recommended_resolution', 'Unknown')}")


if __name__ == '__main__':
    cli()
