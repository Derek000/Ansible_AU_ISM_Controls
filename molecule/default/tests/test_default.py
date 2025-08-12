import os

def test_reports_exist(host):
    assert host.file('/var/tmp/ism_audit').exists
