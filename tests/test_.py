import os
import sys

import numpy as np
from numpy import genfromtxt

from plotting.plotter import Plotter
from src.data_saver import FIEFS_Output
from src.eos import e_EOS, p_EOS
from src.input import FIEFS_Input
from src.mesh import FIEFS_Array, get_interm_array
from src.pgen.kh import ProblemGenerator
from src.pgen.sample import sampleProblemGenerator
from src.reconstruct import get_limited_slopes
from src.tools import (
    get_fluxes_1d,
    get_fluxes_2d,
    get_primitive_variables_1d,
    get_primitive_variables_2d,
)

sys.path.append("..")


def test_FIEFS_input():
    """Test that the parameter input parsing works with kh"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    assert pin.value_dict["rho1"] > pin.value_dict["rho0"]
    assert pin.value_dict["rho0"] > 0.0
    assert pin.value_dict["rho1"] > 0.0
    assert pin.value_dict["p0"] == pin.value_dict["p1"]
    assert pin.value_dict["p0"] > 0.0
    assert pin.value_dict["u0"] >= 0.0
    assert pin.value_dict["u1"] < 0.0
    assert pin.value_dict["pert_amp"] < 1.0
    assert pin.value_dict["pert_amp"] > 0.0
    assert pin.value_dict["CFL"] < 1.0
    assert pin.value_dict["CFL"] > 0.0
    assert pin.value_dict["gamma"] == 1.4
    assert pin.value_dict["left_bc"] == "periodic"
    assert pin.value_dict["right_bc"] == "periodic"
    assert pin.value_dict["top_bc"] == "periodic"
    assert pin.value_dict["bottom_bc"] == "periodic"
    assert float(pin.value_dict["output_frequency"]) >= 1
    assert pin.value_dict["nx1"] >= 64
    assert pin.value_dict["nx2"] >= 64
    assert pin.value_dict["nx1"] == pin.value_dict["nx2"]


def test_FIEFS_pgen():
    """Tests values or signs of values from the problem generator"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    ProblemGenerator(pin=pin, pmesh=pmesh)
    y = np.linspace(
        pin.value_dict["x2min"],
        pin.value_dict["x2max"],
        pin.value_dict["nx2"] + 2 * pin.value_dict["ng"],
    )

    print(y)

    # check that values are correct
    assert np.all(np.isclose(pmesh.Un[0, :, np.abs(y) <= 0.25], 1.0))  # rho0
    assert np.all(np.isclose(pmesh.Un[0, :, np.abs(y) >= 0.25], 2.0))  # rho1
    assert np.all(np.isclose(pmesh.Un[1, :, np.abs(y) <= 0.25], 0.3))  # rho0 * u0
    assert np.all(np.isclose(pmesh.Un[1, :, np.abs(y) >= 0.25], -0.6))  # rho1 * u1

    nx1 = pin.value_dict["nx1"]
    nx2 = pin.value_dict["nx2"]

    # assert pmesh.Un.ndim == (nx1,nx2)
    assert pmesh.Un.shape[0] == 4
    assert pmesh.Un.shape[1] == nx1 + 2 * pin.value_dict["ng"]
    assert pmesh.Un.shape[2] == nx2 + 2 * pin.value_dict["ng"]

    assert np.all(pmesh.Un[3, :, :] >= 0)  # total energy is positive


def test_FIEFS_eos():
    """Tests eos.py by generating random inputs and compares the output of eos.py
    with a direct application of the equation of state equation"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    nx1 = pin.value_dict["nx1"]
    nx2 = pin.value_dict["nx2"]

    correct_pstate = np.empty((nx1, nx2), dtype=float)
    correct_estate = np.empty((nx1, nx2), dtype=float)
    pdiff = np.empty((nx1, nx2), dtype=float)
    ediff = np.empty((nx1, nx2), dtype=float)

    rho = 100.0 * np.random.random_sample(size=(nx1, nx2))
    e = 100.0 * np.random.random_sample(size=(nx1, nx2))
    p = 100.0 * np.random.random_sample(size=(nx1, nx2))

    gamma = 1.4
    pstate = p_EOS(rho, e, gamma)
    assert np.all(pstate > 0.0)

    estate = e_EOS(rho, p, gamma)
    assert np.all(estate > 0.0)

    tol = 0.001
    count = 0.0

    for j in range(nx2):
        for i in range(nx1):
            correct_pstate[i][j] = rho[i][j] * (gamma - 1.0) * e[i][j]
            correct_estate[i][j] = p[i][j] / (rho[i][j] * (gamma - 1.0))

            pdiff[i][j] = abs(pstate[i][j] - correct_pstate[i][j])
            ediff[i][j] = abs(estate[i][j] - correct_estate[i][j])

            if (pdiff[i][j] <= tol) and (ediff[i][j] <= tol):
                count = count + 1

    assert count == (nx1 * nx2)


def test_FIEFS_mesh():
    """Tests that array dimensions in mesh.py are correct"""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    assert np.all(
        pmesh.Un.shape
        == (pmesh.nvar, pmesh.nx1 + 2 * pmesh.ng, pmesh.nx2 + 2 * pmesh.ng)
    )

    interm = get_interm_array(pmesh.nvar, pmesh.nx1, pmesh.nx2, dtype=pmesh.Un.dtype)
    if pmesh.nvar == 1:
        assert np.all(interm.shape == (pmesh.nx1, pmesh.nx2))
    else:
        assert np.all(interm.shape == (pmesh.nvar, pmesh.nx1, pmesh.nx2))


def test_left_bc_enforced():
    """Check left side of domain boundary condition enforcement"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    ng = pin.value_dict["ng"]

    pmesh = FIEFS_Array(pin, np.float64)

    if pin.value_dict["left_bc"] == "transmissive":
        assert np.array_equal(pmesh.Un[:, :ng, :], pmesh.Un[:, ng : 2 * ng, :])

    elif pin.value_dict["left_bc"] == "periodic":
        assert np.array_equal(pmesh.Un[:, :ng, :], pmesh.Un[:, -2 * ng : -ng, :])


def test_right_bc_enforced():
    """Check right side of domain boundary condition enforcement"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    ng = pin.value_dict["ng"]

    pmesh = FIEFS_Array(pin, np.float64)

    if pin.value_dict["right_bc"] == "transmissive":
        assert np.array_equal(pmesh.Un[:, -ng:, :], pmesh.Un[:, -2 * ng : -ng, :])

    elif pin.value_dict["right_bc"] == "periodic":
        assert np.array_equal(pmesh.Un[:, -ng:, :], pmesh.Un[:, ng : 2 * ng, :])


def test_top_bc_enforced():
    """Check top of domain boundary condition enforcement"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    ng = pin.value_dict["ng"]

    pmesh = FIEFS_Array(pin, np.float64)

    if pin.value_dict["top_bc"] == "transmissive":
        assert np.array_equal(pmesh.Un[:, :, :ng], pmesh.Un[:, :, ng : 2 * ng])

    elif pin.value_dict["top_bc"] == "periodic":
        assert np.array_equal(pmesh.Un[:, :ng], pmesh.Un[:, -2 * ng : -ng, :])


def test_bottom_bc_enforced():
    """Check bottom of domain boundary condition enforcement"""

    pin = FIEFS_Input("inputs/kh.in")

    pin.parse_input_file()

    ng = pin.value_dict["ng"]

    pmesh = FIEFS_Array(pin, np.float64)

    if pin.value_dict["bottom_bc"] == "transmissive":
        assert np.array_equal(pmesh.Un[:, :, :ng], pmesh.Un[:, :, ng : 2 * ng])

    elif pin.value_dict["bottom_bc"] == "periodic":
        assert np.array_equal(pmesh.Un[:, :, :ng], pmesh.Un[:, :, -2 * ng : -ng])


def test_FIEFS_reconstruct():
    """Since reconstruct.py essentially finds a linear interpolation
    between values at the cell faces, the slope of the line that it
    finds should have a magnitude of 1 or smaller since our grid is
    made of squares. This test checks for that."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()
    pmesh = FIEFS_Array(pin, np.float64)

    nx1 = pin.value_dict["nx1"]
    nx2 = pin.value_dict["nx2"]
    ng = pin.value_dict["ng"]

    U_i_j = get_interm_array(4, nx1 + (2 * ng - 2), nx2 + (2 * ng - 2), np.float64)
    U_ip1_j = get_interm_array(4, nx1 + (2 * ng - 2), nx2 + (2 * ng - 2), np.float64)
    U_im1_j = get_interm_array(4, nx1 + (2 * ng - 2), nx2 + (2 * ng - 2), np.float64)
    U_i_jp1 = get_interm_array(4, nx1 + (2 * ng - 2), nx2 + (2 * ng - 2), np.float64)
    U_i_jm1 = get_interm_array(4, nx1 + (2 * ng - 2), nx2 + (2 * ng - 2), np.float64)

    U_i_j = pmesh.Un[:, 1:-1, 1:-1]
    U_ip1_j = pmesh.Un[:, 2:, 1:-1]
    U_im1_j = pmesh.Un[:, :-2, 1:-1]
    U_i_jp1 = pmesh.Un[:, 1:-1, 2:]
    U_i_jm1 = pmesh.Un[:, 1:-1, :-2]

    delta_i, delta_j = get_limited_slopes(
        U_i_j, U_ip1_j, U_im1_j, U_i_jp1, U_i_jm1, beta=1.0
    )

    assert np.all(abs(delta_i) <= 1.0)
    assert np.all(abs(delta_j) <= 1.0)


def test_FIEFS_1d_variables():
    """Tests that array dimensions in get_primitive_variables_1d() in
    tools.py are correct."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()
    pmesh = FIEFS_Array(pin, np.float64)

    gamma = pin.value_dict["gamma"]

    nx = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]
    ny = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]

    rho, u, v, p = get_primitive_variables_1d(pmesh.Un, gamma)

    assert rho.size == nx * ny
    assert u.size == nx * ny
    assert v.size == nx * ny
    assert p.size == nx * ny


def test_FIEFS_2d_variables():
    """Tests that array dimensions in get_primitive_variables_2d()
    in tools.py are correct."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()
    pmesh = FIEFS_Array(pin, np.float64)

    gamma = pin.value_dict["gamma"]

    nx = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]
    ny = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]

    rho, u, v, p = get_primitive_variables_2d(pmesh.Un, gamma)

    assert rho.size == nx * ny
    assert u.size == nx * ny
    assert v.size == nx * ny
    assert p.size == nx * ny


def test_FIEFS_1d_fluxes():
    """Tests that array dimensions in get_fluxes_1d() in tools.py are correct."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()
    pmesh = FIEFS_Array(pin, np.float64)

    gamma = pin.value_dict["gamma"]

    nx = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]
    ny = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]

    Fx = get_fluxes_1d(pmesh.Un, gamma, "x")
    assert Fx.size == (pmesh.nvar * nx * ny)

    Fy = get_fluxes_1d(pmesh.Un, gamma, "y")
    assert Fy.size == (pmesh.nvar * nx * ny)


def test_FIEFS_2d_fluxes():
    """Tests that array dimensions in get_fluxes_2d() in tools.py are correct."""

    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()
    pmesh = FIEFS_Array(pin, np.float64)

    gamma = pin.value_dict["gamma"]

    nx = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]
    ny = pin.value_dict["nx1"] + 2 * pin.value_dict["ng"]

    Fx = get_fluxes_2d(pmesh.Un, gamma, "x")
    assert Fx.size == (pmesh.nvar * nx * ny)

    Fy = get_fluxes_2d(pmesh.Un, gamma, "y")
    assert Fy.size == (pmesh.nvar * nx * ny)


def test_FIEFS_data_file_existence():
    """Tests that correct data files exist."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()

    pout = FIEFS_Output("inputs/kh.in")
    pout.data_preferences(pin)

    if "txt" in pout.file_type:
        if "x-velocity" in pout.variables:
            assert os.path.isfile("x-velocity.txt")

        if "y-velocity" in pout.variables:
            assert os.path.isfile("y-velocity.txt")

        if "density" in pout.variables:
            assert os.path.isfile("density.txt")

        if "pressure" in pout.variables:
            assert os.path.isfile("pressure.txt")

    if "csv" in pout.file_type:
        if "x-velocity" in pout.variables:
            assert os.path.isfile("x-velocity.csv")

        if "y-velocity" in pout.variables:
            assert os.path.isfile("y-velocity.csv")

        if "density" in pout.variables:
            assert os.path.isfile("density.csv")

        if "pressure" in pout.variables:
            assert os.path.isfile("pressure.csv")


def test_FIEFS_data_saved_to_file():
    """Tests that array dimensions in FIEFS_data_saver.py are correct."""
    pin = FIEFS_Input("inputs/kh.in")
    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    ProblemGenerator(pin=pin, pmesh=pmesh)

    pout = FIEFS_Output("inputs/kh.in")
    pout.data_preferences(pin)

    nx1 = pin.value_dict["nx1"]
    nx2 = pin.value_dict["nx2"]

    if "txt" in pout.file_type:
        if "x-velocity" in pout.variables:
            data = genfromtxt("x-velocity.txt", delimiter=" ")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "y-velocity" in pout.variables:
            data = genfromtxt("y-velocity.txt", delimiter=" ")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "density" in pout.variables:
            data = genfromtxt("density.txt", delimiter=" ")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "pressure" in pout.variables:
            data = genfromtxt("pressure.txt", delimiter=" ")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

    if "csv" in pout.file_type:
        if "x-velocity" in pout.variables:
            data = genfromtxt("x-velocity.csv", delimiter=",")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "y-velocity" in pout.variables:
            data = genfromtxt("y-velocity.csv", delimiter=",")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "density" in pout.variables:
            data = genfromtxt("density.csv", delimiter=",")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0

        if "pressure" in pout.variables:
            data = genfromtxt("pressure.csv", delimiter=",")

            assert data.ndim == (nx1, nx2)
            assert data.size % nx1 == 0


def test_plotter_directory():
    """Remove directory if it exists to test the plotter's ability to create it"""

    if os.path.exists("./output/plots"):
        if len(os.listdir("./output/plots")):
            for file in os.scandir("./output/plots"):
                os.remove(file.path)
        os.removedirs("./output/plots")

    assert not os.path.exists("./output/plots")

    pin = FIEFS_Input("inputs/sample.in")

    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    sampleProblemGenerator(pin=pin, pmesh=pmesh)

    test_plotter = Plotter(pmesh)
    test_plotter.check_path_exists()

    assert os.path.exists("./output/plots")


def test_plotter_init():
    """Initialize plotter with sample data and verify it loads the correct data in"""

    pin = FIEFS_Input("inputs/sample.in")

    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    sampleProblemGenerator(pin=pin, pmesh=pmesh)

    test_plotter = Plotter(pmesh)

    assert np.ceil(test_plotter.x1[-1]) == pmesh.x1max
    assert np.ceil(test_plotter.x2[-1]) == pmesh.x2max

    # Pick a random point to test
    randint_x1 = np.random.randint(0, len(test_plotter.x1))
    randint_x2 = np.random.randint(0, len(test_plotter.x2))

    assert test_plotter.ng == pmesh.ng
    assert (
        test_plotter.rho[randint_x1, randint_x2] == pmesh.Un[0, randint_x1, randint_x2]
    )
    assert (
        test_plotter.rho[randint_x1, randint_x2]
        * test_plotter.u[randint_x1, randint_x2]
        == pmesh.Un[1, randint_x1, randint_x2]
    )
    assert (
        test_plotter.rho[randint_x1, randint_x2]
        * test_plotter.v[randint_x1, randint_x2]
        == pmesh.Un[2, randint_x1, randint_x2]
    )
    assert (
        test_plotter.rho[randint_x1, randint_x2]
        * test_plotter.et[randint_x1, randint_x2]
        == pmesh.Un[3, randint_x1, randint_x2]
    )


def test_plotter_figure():
    """Initialize plotter with sample data and verify it generates a figure"""

    pin = FIEFS_Input("inputs/sample.in")

    pin.parse_input_file()

    pmesh = FIEFS_Array(pin, np.float64)

    sampleProblemGenerator(pin=pin, pmesh=pmesh)

    test_plotter = Plotter(pmesh)

    test_plotter.create_plot(
        ["rho"],
        ["test"],
        ["magma"],  # the coolest cmap by the way
        stability_name="test",
        style_mode=True,
        iter=1,
        time=0,
    )

    assert os.path.exists("./output/plots/0001.png")

    os.remove("./output/plots/0001.png")
