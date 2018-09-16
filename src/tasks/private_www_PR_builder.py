from .github_base import PyGithubTask

class private_www_PR_builder(PyGithubTask):
    LABEL = "private_www_PR_builder"
    def __init__(self,config,**kwargs):
        """
        Extract parameters specific to this task:
            name:       Name of this task (LABEL by default)
            temp_dir:   Temporary directory where this task will be run
        """
        LABEL = self.LABEL
        super().__init__(config,**kwargs)
        super().get_name(config,LABEL)
        super().get_temp_dir(config,LABEL)
        super().get_repo_whitelist(config,LABEL)

    def run(self,payload,meta,config):
        super().run(payload,meta,config)



