from multi_agents import agents
import yaml


# vespa config
with open('conf/ext_services.yaml', 'r') as f:
    ext_service_config = yaml.safe_load(f)
