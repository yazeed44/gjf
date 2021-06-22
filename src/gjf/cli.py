import logging
import os
import click
import geojson

from gjf import logger, __version__
from gjf.geojson_fixer import validity, apply_fixes_if_needed


def handle_overwrite(geojson_files, fixed_geometries):
    file_paths = [file.name for file in geojson_files]
    for path, geometry in zip(file_paths, fixed_geometries):
        with open(path, 'w') as f:
            geojson.dump(geometry, f, ensure_ascii=False)
    click.echo(os.linesep.join([f"Wrote fixes to {path}" for path in file_paths]))


def handle_new_file(geojson_files, fixed_geometries, postfix="_fixed"):
    new_file_paths = [os.path.splitext(file.name)[0] + postfix + os.path.splitext(file.name)[-1] for file in
                      geojson_files]
    for path, geometry in zip(new_file_paths, fixed_geometries):
        with open(path, 'w') as f:
            geojson.dump(geometry, f, ensure_ascii=False)
    click.echo(os.linesep.join([f"Wrote fixes to {path}" for path in new_file_paths]))


@click.command()
@click.version_option(version=__version__)
@click.argument("geojson-files", nargs=-1, type=click.File())
@click.option("--validate/--fix", default=False,
              help="If --validate is triggered, the validity of the file(s) will be printed without fixing. Otherwise will attempt to fix the file ")
@click.option("-v", "--verbosity",
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False))
@click.option("-o", "--output-method", default="new_file", type=click.Choice(["overwrite", "new_file", "print"]),
              help="Choose how to output the fixed geometry; Overwriting the source file, or by creating a new file, or print it on the screen")
@click.option("--flip/--no-flip", default=False,
              help="Choose whether to flip coordinates order. For example, from [25, 50] to [50, 25]")
def main(geojson_files, validate, verbosity, output_method, flip):
    if verbosity:
        logger.setLevel(level=getattr(logging, verbosity.upper(), "NOTSET"))
    logger.debug("Started CLI with following parameters: validate: %s, verbosity: %s, output_method: %s, flip: %s", validate, verbosity, output_method, flip)
    if validate:
        click.echo(os.linesep.join([str(validity(geojson.load(file))) for file in geojson_files]))
    else:
        output_method = output_method.lower()
        fixed_geometries = [apply_fixes_if_needed(geojson.load(file), flip_coords=flip) for file in
                            geojson_files]
        if output_method == "overwrite":
            handle_overwrite(geojson_files, fixed_geometries)
        elif output_method == "new_file":
            handle_new_file(geojson_files, fixed_geometries)
        elif output_method == "print":
            click.echo(os.linesep.join([str(geometry) for geometry in fixed_geometries]))


if __name__ == "__main__":
    main()
