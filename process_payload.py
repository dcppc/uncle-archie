from hooks.dump_payload                     import process_payload as dump_payload
from hooks.rubber_stamp                     import process_payload as rubber_stamp
from hooks.mkdocs_build_test                import process_payload as mkdocs_build_test
from hooks.private_www_integration_test     import process_payload as private_www_integration_test
from hooks.private_www_build_test           import process_payload as private_www_build_test
from hooks.ucl_snakemake_test               import process_payload as ucl_snakemake_test
from hooks.search_demo_update_submodules    import process_payload as search_demo_update_submodules
from hooks.private_www_update_submodules    import process_payload as private_www_update_submodules

def process_payload(payload,meta,config):
    dump_payload(payload,meta,config)
    rubber_stamp(payload,meta,config)
    mkdocs_build_test(payload,meta,config)
    private_www_integration_test(payload,meta,config)
    private_www_build_test(payload,meta,config)
    ucl_snakemake_test(payload,meta,config)
    search_demo_update_submodules(payload,meta,config)
    private_www_update_submodules(payload,meta,config)

if __name__=="__main__":
    process_payload({'type':'test','name':'process_payload'},{'a':1,'b':2})

