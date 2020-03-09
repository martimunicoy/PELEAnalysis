# Project imports
from PELETools.TimeCalculator.PELEStepTypes import Step, Perturbation, WaterPerturbation, ANM,\
    SideChain, Minimization, PELE_STEP_TYPES_DICT

# Libraries imports
from nose.tools import assert_equal, assert_in, assert_is


class TestPELEStepTypes:

    def test_step_init(self):
        step = Step()
        assert_equal(step.name, "Step")
        assert_equal(step.name_to_search_in_log_file, "step time")
        assert_equal(step.time_position_in_log_file, 0)

    def test_perturbation_init(self):
        perturbation = Perturbation()
        assert_equal(perturbation.name, "Perturbation")
        assert_equal(perturbation.name_to_search_in_log_file, "Perturbation Ef:")
        assert_equal(perturbation.time_position_in_log_file, -1)

    def test_water_perturbation_init(self):
        perturbation = WaterPerturbation()
        assert_equal(perturbation.name, "Water Perturbation")
        assert_equal(perturbation.name_to_search_in_log_file, "Water perturbation: Ef:")
        assert_equal(perturbation.time_position_in_log_file, -1)

    def test_anm_init(self):
        anm = ANM()
        assert_equal(anm.name, "ANM")
        assert_equal(anm.name_to_search_in_log_file, "ANM Ef:")
        assert_equal(anm.time_position_in_log_file, -1)

    def test_side_chain_init(self):
        side_chain = SideChain()
        assert_equal(side_chain.name, "SideChain")
        assert_equal(side_chain.name_to_search_in_log_file, "Side Chain Prediction Ef")
        assert_equal(side_chain.time_position_in_log_file, -1)

    def test_minimization_init(self):
        minimization = Minimization()
        assert_equal(minimization.name, "Minimization")
        assert_equal(minimization.name_to_search_in_log_file, "Minimization Ef:")
        assert_equal(minimization.time_position_in_log_file, -1)

    def test_step_types_dict(self):
        assert_in("Step", PELE_STEP_TYPES_DICT)
        assert_in("Perturbation", PELE_STEP_TYPES_DICT)
        assert_in("ANM", PELE_STEP_TYPES_DICT)
        assert_in("SideChain", PELE_STEP_TYPES_DICT)
        assert_in("Minimization", PELE_STEP_TYPES_DICT)

    def test_step_types_references(self):
        assert_is(PELE_STEP_TYPES_DICT["Step"], Step)
        assert_is(PELE_STEP_TYPES_DICT["Perturbation"], Perturbation)
        assert_is(PELE_STEP_TYPES_DICT["ANM"], ANM)
        assert_is(PELE_STEP_TYPES_DICT["SideChain"], SideChain)
        assert_is(PELE_STEP_TYPES_DICT["Minimization"], Minimization)
