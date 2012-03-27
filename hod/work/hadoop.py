from hod.work.work import Work

class Hadoop(Work):
    """Base Hadoop work class"""
    def __init__(self, ranks):
        Work.__init__(self, ranks)

        self.version = {'major':-1,
                      'minor':-1}

        self.home = None
        self.hadoop = None

        ## some default initialisation        
        self.which_hadoop()

    def which_hadoop(self):
        """Locate HADOOP_HOME and hadoop"""

    def hadoop_version(self):
        """Set the major and minor version"""

    def is_version(self, req=None):
        """Given a requirement req, check if current version is sufficient"""

    def locate_start_stop(self):
        """Try to locate for the start and stop scripts"""

    def prepare_location(self):
        """prepare the location: make directories etc"""

    def prepare_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""

    def prepare_env(self):
        """prepare the environment: collect the parameters and make env vars"""

    def start_service_master(self):
        """Start the Hadoop service"""

    def post_start_master(self):
        """Run after start_service_master"""

    def post_start_all(self):
        """Run after start_service"""

    def stop_service_master(self):
        """Stop the Hadoop service"""

    def post_stop_master(self):
        """Run after start_service_master"""

    def post_stop_all(self):
        """Run after start_service"""

    def wait(self):
        """What to do between start and stop"""

    def do_work(self):
        """Look for required code and prepare all"""

        self.prepare_location()
        self.prepare_cfg()
        self.prepare_env()

        self.barrier("Going to run master only")
        if self.rank == self.masterrank:
            self.locate_start_stop()
            self.start_service_master()
            self.post_start_master()

        self.barrier("Going to run post_start all")
        self.post_start_all()

        self.barrier("Going to wait all")
        self.wait()

        self.barrier("Going to stop ")
        if self.rank == self.masterrank:
            self.stop_service_master()
            self.post_stop_master()

        self.barrier("Going to run post_stop all")
        self.post_stop_all()

