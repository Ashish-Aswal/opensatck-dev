# Copyright (c) 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging

from nova.scheduler import filters
from nova.scheduler.filters import utils

from nova.api.openstack import common
from nova.compute import api as compute

LOG = logging.getLogger(__name__)


class NumCoresCustomFilter(filters.BaseHostFilter):
    """Filter out hosts with number of cores less than length of scheduled vm's name."""

    RUN_ON_REBUILD = False

    def __init__(self):
        self.compute_api = compute.API()


    #TODO : This should be under some decorator for compute.API() failures.
    def _get_requested_vm_name(self, spec_obj):
        """ returns display name for the scheduled vm """

        req_context  = spec_obj._context
        req_vm_uuid  = spec_obj.instance_uuid
        req_instance = common.get_instance(self.compute_api, req_context, req_vm_uuid)

        return req_instance._obj_display_name if req_instance._obj_display_name else None


    def host_passes(self, host_state, spec_obj):
        num_cpus    = int(host_state.vcpus_total)
        len_vm_name = len(self._get_requested_vm_name(spec_obj))

        passes = len_vm_name < num_cpus

        if not passes:
            LOG.debug("%(host_state)s fails num_cores check : vm's name length "
                    "%(len_vm_name)s must be less than host's cpu cores %(num_cpus)s",
                    {'host_state': host_state, 'len_vm_name': len_vm_name, 'num_cpus': num_cpus})

        return passes
