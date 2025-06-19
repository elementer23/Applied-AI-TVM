from tvm.tools.db_tool import CustomAdvisoryDatabaseTool


def test_get_advisory_text():
    tool = CustomAdvisoryDatabaseTool()
    category = "damage_to_third_parties"
    sub_category = "minrisk"
    expected_text = """Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om alle trekkers + opleggers WA volledig casco te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]

Onderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.
WA:
- Hulpverlening bij ziekte of ongeval
- Gladheidsbestrijding
- Vervoer van gevaarlijke stoffen
- Werkrisico
- Gemonteerd werkmaterieel
Brand, brand/diefstal, beperkt casco of volledig casco:
- Berging en repatriÃ«ring
Volledig Casco:
- Bergingskosten na pech"""

    result = tool._run(category=category, sub_category=sub_category)

    assert result == expected_text
