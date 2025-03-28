from faker import Faker
from faker.providers import DynamicProvider

law_problem_prodider = DynamicProvider(
    provider_name="law_problem",
    eleements = []
)

fire_problem_prodider = DynamicProvider(
    provider_name="fire_problem",
    elements = []
)

ems_problem_prodider = DynamicProvider(
    provider_name="ems_problem",
    elements = []
)

fake = Faker()