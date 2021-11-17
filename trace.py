
def read_requirements():
    with open('requirements.txt') as req:
        content = req.read()
        requirements = content.split('\n')
    return requirements

def import_from(module, name):
    try:
        module = __import__(module, fromlist=[name])
    except ModuleNotFoundError as e:
        raise e
    return getattr(module, name)

def get_additional_instrument():
    packages = read_requirements()
    instrument = {
        'psycopg2': {'opentelemetry.instrumentation.psycopg2': 'Psycopg2Instrumentor'},
        'SQLAlchemy': {'opentelemetry.instrumentation.sqlalchemy': 'SQLAlchemyInstrumentor'},
        'requests': {'opentelemetry.instrumentation.requests': 'RequestsInstrumentor'}
        }
    for p in packages:
        package_name = p.split('==')[0]
        required_instrument = instrument.get(package_name, '')
        if required_instrument:
            module = list((required_instrument.keys()))[0]
            name = list((required_instrument.values()))[0]
            attr = import_from(module, name)
            attr().instrument()
