"""
HDFS config and options
"""

from hod.config.customtypes import HostnamePort, Directories, Arguments, ParamsDescr, UserGroup, Boolean

from hod.config.hadoopopts import HadoopOpts
from hod.config.hadoopcfg import HadoopCfg


## namenode is set in core
HDFS_OPTS = ParamsDescr({
    'dfs.name.dir':[Directories([None]), 'Determines where on the local filesystem the DFS name node should store the name table(fsimage). If this is a comma-delimited list of kindoflist then the name table is replicated in all of the kindoflist, for redundancy. def ${hadoop.tmp.dir}/dfs/name'],
    'dfs.data.dir':[Directories([None]), 'Determines where on the local filesystem an DFS data node should store its blocks. If this is a comma-delimited list of kindoflist, then data will be stored in all named kindoflist, typically on different devices. Directories that do not exist are ignored. def ${hadoop.tmp.dir}/dfs/data'],

    'dfs.datanode.address':[HostnamePort(':50090'), 'The address where the datanode server will listen to. If the port is 0 then the server will start on a free port.'],
    'dfs.datanode.ipc.address':[HostnamePort(':50020'), 'The datanode ipc server address and port. If the port is 0 then the server will start on a free port.'],
})

HDFS_SECURITY_SERVICE = ParamsDescr({
    'security.client.protocol.acl':[UserGroup(), 'ACL for ClientProtocol, which is used by user code via the DistributedFileSystem.'],
    'security.client.datanode.protocol.acl':[UserGroup(), 'ACL for ClientDatanodeProtocol, the client - to - datanode protocol for block recovery.'],
    'security.datanode.protocol.acl':[UserGroup(), 'ACL for DatanodeProtocol, which is used by datanodes to communicate with the namenode.'],
    'security.inter.datanode.protocol.acl':[UserGroup(), 'ACL for InterDatanodeProtocol, the inter - datanode protocol for updating generation timestamp.'],
    'security.namenode.protocol.acl':[UserGroup(), 'ACL for NamenodeProtocol, the protocol used by the secondary namenode to communicate with the namenode.'],
})

HDFS_HTTP_OPTS = ParamsDescr({
    'dfs.namenode.http-address':[HostnamePort(':50070'), 'The address and the base port where the dfs namenode web ui will listen on. If the port is 0 then the server will start on a free port.'],
    'dfs.datanode.http.address':[HostnamePort(':50075'), 'The datanode http server address and port. If the port is 0 then the server will start on a free port.'],
})

HDFS_ENV_OPTS = ParamsDescr({
    'HADOOP_NAMENODE_OPTS':[Arguments("-XX:+UseParallelGC"), ''],
    'HADOOP_DATANODE_OPTS':[Arguments(), ''],
    'HADOOP_SECONDARYNAMENODE_OPTS':[Arguments(), ''],
})

HDFS_HBASE_OPTS = ParamsDescr({
    'dfs.support.append':[Boolean(True), 'Enable durable sync'],
    'dfs.datanode.max.xcievers':[4096, 'Number of files to served at any one time.'],
})

class HdfsCfg(HadoopCfg):
    """Hdfs cfg"""
    def __init__(self):
        HadoopCfg.__init__(self)
        self.name = 'dfs'

class HdfsOpts(HdfsCfg, HadoopOpts):
    """Hdfs options"""
    def __init__(self, shared=None, basedir=None):
        self.format_hdfs = True

        HadoopOpts.__init__(self, shared=shared, basedir=basedir)
        HdfsCfg.__init__(self)


    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(HDFS_OPTS)
        if self.shared_opts['other_work'].get('Hbase', False): ## HBase is not active here
            self.log.debug("Adding Hbase HDFS params")
            self.add_from_opts_dict(HDFS_HBASE_OPTS)


    def init_security_defaults(self):
        """Add security options"""
        self.log.debug("Add HDFS security settings")
        self.add_from_opts_dict(HDFS_SECURITY_SERVICE)

