import nox
import os

# Define the versions you want to test against
python_versions = ["3.9", "3.10", "3.11"]

#@nox.session(python=python_versions)
#def tests(session: nox.Session) -> None:
#    """
#    Run the unit and regular tests.
#    """
#    session.install(".[test]")
#    session.run("pytest")

@nox.session(python="/path/to/python3.11")
def tests(session: nox.Session) -> None:
    session.install(".[test]")
    session.run("pytest")

@nox.session(python="3.11")
def lint(session):
    session.install("flake8")
    session.run("flake8", "src/")

@nox.session(python="3.11")
def docs(session: nox.Session) -> None:
    """
    Build the docs. Pass "--serve" to serve.
    """
    session.install(".[docs]")
    session.chdir("docs")
    session.run("sphinx-build", "-M", "html", ".", "_build")

@nox.session(python="3.11")
def serve(session: nox.Session) -> None:
    docs(session)
    print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
    session.run("python", "-m", "http.server", "8000", "-d", "_build/html")
