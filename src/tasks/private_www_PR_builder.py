from .github_base import PyGithubTask

class private_www_PR_builder(PyGithubTask):
    # Once this is defined, the parent constructor
    # will be able to extract task-specific config
    # parameters for us. Nice!
    LABEL = "private_www_PR_builder"

    def run(self,payload,meta,config):
        super().run(payload,meta,config)



