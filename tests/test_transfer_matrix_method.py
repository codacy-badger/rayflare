from pytest import mark, approx
import numpy as np

def test_tmm_structure():
    from rayflare.transfer_matrix_method import tmm_structure


    tmm_setup = tmm_structure([])
    RAT = tmm_setup.calculate(wavelength=np.array([]))


    assert sorted(list(RAT.keys())) == ["A", "A_per_layer", "R", "T", "all_p", "all_s"]


def test_tmm_structure_abs():
    import numpy as np
    from solcore import si, material
    from solcore.structure import Layer
    from rayflare.transfer_matrix_method import tmm_structure
    from solcore.solar_cell import SolarCell
    from solcore.constants import q, h, c

    InGaP = material('GaInP')(In=0.5)
    GaAs = material('GaAs')()
    Ge = material('Ge')()
    Ag = material('Ag')()
    Air = material('Air')()

    Al2O3 = material('Al2O3')()

    # anti-reflection coating

    wavelengths = np.linspace(250, 1900, 200) * 1e-9

    RCWA_wl = wavelengths

    options = {'pol': 's',
               'wavelengths': RCWA_wl,
               'parallel': True,
               'n_jobs': -1,
               'theta_in': 0,
               'phi_in': 0,
               'A_per_order': False}

    ARC = [Layer(si('80nm'), Al2O3)]

    solar_cell = SolarCell(ARC + [Layer(material=InGaP, width=si('400nm')),
                                  Layer(material=GaAs, width=si('4000nm')),
                                  Layer(material=Ge, width=si('3000nm'))], substrate=Ag)

    tmm_setup = tmm_structure(solar_cell, coherent=True)

    integrated = np.zeros((6, 3))
    j1 = 0
    for pol in ['s', 'p', 'u']:
        for angle in [0, 60]:
            options['pol'] = pol
            options['theta_in'] = angle

            tmm_result = tmm_setup.calculate(wavelength=wavelengths * 1e9, pol=pol, angle=angle * np.pi / 180)

            integr = 1e4*np.trapz(
                wavelengths[:, None] * 1e9 * tmm_result['A_per_layer'],
                wavelengths * 1e9, axis=0) / 1e9

            integrated[j1, :] = integr[1:]

            j1 += 1

    expected = np.array([[1.4234972 , 1.67748004, 7.35621745],
       [1.35543244, 1.30592315, 5.28228305],
       [1.4234972 , 1.67748004, 7.35621745],
       [1.44652436, 1.65923102, 8.43831573],
       [1.4234972 , 1.67748004, 7.35621745],
       [1.4009784 , 1.48257709, 6.86029939]])
    assert approx(integrated == expected)


