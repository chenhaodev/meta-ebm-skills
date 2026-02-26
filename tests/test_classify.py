# tests/test_classify.py
from builder.classify import classify_topic

def test_overview_topics():
    assert classify_topic("An overview of asthma management") == "overview"
    assert classify_topic("Pathogenesis of asthma") == "overview"
    assert classify_topic("Epidemiology of asthma") == "overview"

def test_diagnosis_topics():
    assert classify_topic("Diagnosis of asthma in adolescents and adults") == "diagnosis"
    assert classify_topic("Evaluation of severe asthma") == "diagnosis"
    assert classify_topic("Pulmonary function testing in asthma") == "diagnosis"

def test_treatment_topics():
    assert classify_topic("Treatment of severe asthma in adolescents") == "treatment"
    assert classify_topic("Management of acute exacerbations of asthma") == "treatment"
    assert classify_topic("Beta agonists in asthma") == "treatment"

def test_monitoring_topics():
    assert classify_topic("Peak expiratory flow rate monitoring in asthma") == "monitoring"
    assert classify_topic("Enhancing patient adherence to asthma therapy") == "monitoring"

def test_drugs_topics():
    assert classify_topic("Albuterol: Drug information") == "drugs"
    assert classify_topic("Fluticasone: Pediatric drug information") == "drugs"
    assert classify_topic("Prednisone: Patient drug information") == "drugs"

def test_fallback_to_overview():
    assert classify_topic("Some unrecognized title about breathing") == "overview"
