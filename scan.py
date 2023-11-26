import typer

from resources.decorators import logtime
from resources.models import JobsAndProfileSchema
from scanners.upwork import UpWorkScanner
from settings import logger as log
from utils.file_utils import export_json

app = typer.Typer(help="CLI to execute scanners.")


@logtime('SCANNER')
@app.command()
def upwork(export: str = 'json'):
    """Execute the scanner of upwork.com"""
    info = {
        'username': 'recruitment+scanners+task@argyle.com',
        'username_backup_one': 'recruitment+scanners+data@argyle.com',
        'username_backup_two': 'recruitment+tasks@argyle.com',
        'password': 'ArgyleAwesome!@',
        'secret_answer': 'Jimmy'
    }
    scanner = UpWorkScanner(info)
    scanner.run()
    if scanner.scanned_data:
        match export:
            case 'json':
                jobs = scanner.scanned_data['jobs']
                profile = scanner.scanned_data['profile']
                jobs_and_profile = JobsAndProfileSchema(jobs=jobs, profile=profile)
                export_json(jobs_and_profile.model_dump_json(indent=2), filename='upwork')
            case _:
                log.warning('Type of format to export not accepted.')
    else:
        log.warning(f'There is no information to be exported '
                    f'in a {export} file')


@app.command()
def another_scanner(export: str = 'json'):
    ...


if '__main__' == __name__:
    app()
