"""
HDFS config and options
"""

from hod.config.types import *
from hod.config.hadoopopts import HadoopOpts
from hod.config.hadoopcfg import HadoopCfg

## namenode is set in core
HDFS_OPTS = {
    'dfs.replication' : [1, 'Default block replication. The actual number of replications can be specified when the file is created. The default is used if replication is not specified in create time.'],

    'dfs.name.dir':[Directories([None]), 'Determines where on the local filesystem the DFS name node should store the name table(fsimage). If this is a comma-delimited list of kindoflist then the name table is replicated in all of the kindoflist, for redundancy. def ${hadoop.tmp.dir}/dfs/name'],
    'dfs.data.dir':[Directories([None]), 'Determines where on the local filesystem an DFS data node should store its blocks. If this is a comma-delimited list of kindoflist, then data will be stored in all named kindoflist, typically on different devices. Directories that do not exist are ignored. def ${hadoop.tmp.dir}/dfs/data'],

    'dfs.datanode.address':[HostnamePort('0.0.0.0:50090'), 'The address where the datanode server will listen to. If the port is 0 then the server will start on a free port.'],
    'dfs.datanode.http.address':[HostnamePort('0.0.0.0:50075'), 'The datanode http server address and port. If the port is 0 then the server will start on a free port.'],
    'dfs.datanode.ipc.address':[HostnamePort('0.0.0.0:50020'), 'The datanode ipc server address and port. If the port is 0 then the server will start on a free port.'],
    'dfs.namenode.http-address':[HostnamePort('0.0.0.0:50070'), 'The address and the base port where the dfs namenode web ui will listen on. If the port is 0 then the server will start on a free port.'],
}

HDFS_ENV_OPTS = {
    'HADOOP_NAMENODE_OPTS':[Arguments(), ''],
    'HADOOP_DATANODE_OPTS':[Arguments(), ''],
    'HADOOP_SECONDARYNAMENODE_OPTS':[Arguments(), ''],
}


class HdfsOpts(HadoopOpts):
    """Hdfs options"""

    def defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding defaults.")
        self.add_from_opts_dict(HDFS_OPTS)



class HdfsCfg(HadoopCfg):
    """Hdfs cfg"""

