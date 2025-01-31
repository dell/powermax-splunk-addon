# Copyright (c) 2021 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""test_pyu4v_ci_replication.py."""
import testtools
import time

from PyU4V.tests.ci_tests import base


class CITestReplication(base.TestBaseTestCase, testtools.TestCase):
    """Test Replication Functions."""

    def setUp(self):
        """SetUp."""
        super(CITestReplication, self).setUp()
        self.replication = self.conn.replication
        self.provisioning = self.conn.provisioning
        self.system = self.conn.system
        self.is_v4 = self.common.is_array_v4(self.conn.array_id)

    def test_get_array_replication_capabilities(self):
        """Test get_array_replication_capabilities."""
        rep_info = self.conn.replication.get_array_replication_capabilities(
            array_id=self.conn.array_id)
        self.assertEqual(9, len(rep_info.keys()))
        assert 'symmetrixId' in rep_info
        assert 'snapVxCapable' in rep_info
        assert 'rdfCapable' in rep_info
        assert 'witness_capable' in rep_info
        assert 'virtual_witness_capable' in rep_info
        assert 'snapshot_policy_capable' in rep_info
        assert 'metro_dr_capable' in rep_info
        assert 'vasa_async_remote_rep_capable' in rep_info
        assert 'metro_capable' in rep_info

    def test_is_snapvx_licensed(self):
        """Test is_snapvx_licensed."""
        licensed = self.replication.is_snapvx_licensed()
        self.assertIs(True, licensed)

    def test_get_storage_group_replication_details(self):
        """Test get_storage_group_rep."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        rep_info = self.replication.get_storage_group_replication_details(
            storage_group_id=sg_name)
        self.assertEqual(1, rep_info.get('numSnapVXSnapshots'))

    def test_get_storage_group_replication_details_srdf_details(self):
        """Test get_storage_group_rep."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rep_info = self.replication.get_storage_group_replication_details(
            storage_group_id=sg_name, return_remote_sg_info=True,
            exclude_sl_snaps=True, exclude_manual_snaps=True)
        remote_storage_group = rep_info.get('remote_storage_groups')[0]
        self.assertEqual(sg_name, remote_storage_group.get('storage_group_id'))

    def test_create_storage_group_snapshot(self):
        """Test get_storagegroup_snapshot_list."""
        if self.is_v4:
            self.skipTest('Create storage group snapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        self.replication.create_storage_group_snapshot(
            sg_name, 'ci_snap', ttl=1, hours=True)
        snapshot_info = self.replication.get_storage_group_snapshot_list(
            sg_name)
        snapshot_details = (
            self.replication.get_storage_group_snapshot_generation_list(
                sg_name, snap_name='ci_snap'))
        self.replication.delete_storage_group_snapshot(
            sg_name, snap_name='ci_snap', gen=(snapshot_details[0]))
        self.assertIn('ci_snap', snapshot_info)

    def test_create_storage_group_snapshot_by_snap_id(self):
        """Test create_storage_group_snapshot by snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        ss_name = self.generate_name(object_type='ss')
        self.replication.create_storage_group_snapshot(
            sg_name, ss_name, ttl=1, hours=True)
        snapshot_info = self.replication.get_storage_group_snapshot_list(
            sg_name)
        snapshot_details = (
            self.replication.get_storage_group_snapshot_snap_id_list(
                sg_name, ss_name))
        self.replication.delete_storage_group_snapshot_by_snap_id(
            sg_name, ss_name, snapshot_details[0])
        self.assertIn(ss_name, snapshot_info)

    def test_get_replication_enabled_storage_groups(self):
        """Test get_replication_enabled_storage_groups."""
        self.create_sg_snapshot()
        snap_list = self.replication.get_replication_enabled_storage_groups(
            has_snapshots=True, has_srdf=False)
        self.assertIsInstance(snap_list, list)

    def test_get_storage_group_snapshot_list(self):
        """Test get_storage_group_snapshot_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        sg_snap_list = self.replication.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        self.assertEqual(snapshot_info.get('name'), sg_snap_list[0])

    def test_get_storage_group_no_snapshot(self):
        """Test get_storagegroup_snapshot_list."""
        storage_group_name = self.generate_name('sg')
        volume_name = self.generate_name()
        self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO,
            vol_name=volume_name)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self.assertFalse(self.replication.get_storage_group_snapshot_list(
            storage_group_name))

    def test_modify_storage_group_snapshot_rename(self):
        """Test modify_storage_group_snapshot."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does  '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        snapshot_details = (
            self.replication.get_storage_group_snapshot_generation_list(
                sg_name, snap_name=old_name))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=old_name, new_name='newname',
            gen_num=snapshot_details[0])
        snap_list = self.replication.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        # change name back so clean up will work automatically
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name='newname', new_name=old_name,
            gen_num=snapshot_details[0])
        self.assertEqual('newname', snap_list[0])

    def test_modify_storage_group_snap_rename_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        new_name = self.generate_name(object_type='ss')
        snapshot_details = (
            self.replication.get_storage_group_snapshot_snap_id_list(
                sg_name, old_name))
        snap_id = snapshot_details[0]
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, old_name, snap_id,
            new_name=new_name)
        snap_list = self.replication.get_storage_group_snapshot_list(
            sg_name)
        # change name back so clean up will work automatically
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, new_name, snap_id, new_name=old_name)
        self.assertEqual(new_name, snap_list[0])

    def test_get_replication_info(self):
        """Test get_replication_info."""
        array_id = self.conn.array_id
        rep_info = self.replication.get_replication_info()
        self.assertEqual(array_id, rep_info.get('symmetrixId'))
        assert 'storageGroupCount' in rep_info
        assert 'replicationCacheUsage' in rep_info

    def test_modify_storage_group_snapshot_link(self):
        """Test to cover link snapshot."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot link by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertEqual(True, snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snap_relink(self):
        """Test to cover relink snapshot."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot relink by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, relink=True)
        relink_snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(relink_snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snap_link_by_snap_id(self):
        """Test to cover link snapshot by snap id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snap_relink_by_snap_id(self):
        """Test to cover relink snapshot by snap id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, relink=True)
        relink_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(relink_snap_details.get('linked'))
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snapshot_unlink(self):
        """Test to cover unlink snapshot."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot unlink by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, link=True)
        linked_snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(linked_snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_modify_storage_group_snapshot_unlink_by_snap_id(self):
        """Test modify_storage_group_snapshot unlink snapshot by snap id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, link=True)
        linked_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(linked_snap_details.get('linked'))
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_modify_storage_group_snapshot_restore(self):
        """Test modify_storage_group_snapshot restore snapshot."""
        if self.is_v4:
            self.skipTest(
                'Modify storage group snapshot restore by generation does '
                'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=None,
            snap_name=snap_name, gen_num=0, restore=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_modify_storage_group_snap_restore_by_snap_id(self):
        """Test to cover restore snapshot by snap id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, None, snap_name, snap_id, restore=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_restored=True)

        self.assertTrue('Restored' in snap_details.get('state'))

    def test_restore_snapshot(self):
        """Test to cover restore snapshot."""
        if self.is_v4:
            self.skipTest('Restore snapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        self.replication.restore_snapshot(sg_id=sg_name,
                                          snap_name=snap_name, gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_restore_snapshot_by_snap_id(self):
        """Test to cover restore snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.restore_snapshot_by_snap_id(
            sg_name, snap_name, snap_id)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_restored=True)
        self.assertTrue('Restored' in snap_details.get('state'))

    def test_rename_snapshot(self):
        """Test to cover rename snapshot."""
        if self.is_v4:
            self.skipTest('Rename shapshot by generation does '
                          'not work on the V4.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        self.replication.rename_snapshot(
            sg_id=sg_name, snap_name=old_name, new_name='newname', gen_num=0)
        snap_list = self.replication.get_storage_group_snapshot_list(
            storage_group_id=sg_name)
        self.assertEqual('newname', snap_list[0])
        # change name back so clean up will work automatically
        self.replication.rename_snapshot(
            sg_id=sg_name, snap_name='newname', new_name=old_name,
            gen_num=0)

    def test_rename_snapshot_by_snap_id(self):
        """Test to cover rename snapshot by snap_id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        old_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        new_name = self.generate_name(object_type='ss')
        self.replication.rename_snapshot_by_snap_id(
            sg_name, old_name, new_name, snap_id)
        snap_list = self.replication.get_storage_group_snapshot_list(
            sg_name)
        self.assertEqual(new_name, snap_list[0])
        # change name back so clean up will work automatically
        self.replication.rename_snapshot_by_snap_id(
            sg_name, new_name, old_name, snap_id)

    def _test_get_ss_gen_detail(
            self, sg_name, snap_name, gen_num, check_linked=False,
            check_unlinked=False, check_restored=False):
        time.sleep(1)
        snap_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=gen_num)
        i = 0
        if check_unlinked:
            while snap_details.get('isLinked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to unlink" % i)
                snap_details = (
                    self.replication.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        elif check_linked:
            while not snap_details.get('isLinked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to link" % i)
                snap_details = (
                    self.replication.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        elif check_restored:
            while 'Restored' not in snap_details.get('state'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to restore" % i)
                snap_details = (
                    self.replication.get_snapshot_generation_details(
                        sg_id=sg_name, snap_name=snap_name, gen_num=gen_num))
                if i > 10:
                    break
        else:
            print("WARNING - no check set so polling can not occur.")
        return snap_details

    def _test_get_ss_snapid_detail(
            self, sg_name, snap_name, snap_id, check_linked=False,
            check_unlinked=False, check_restored=False):
        time.sleep(1)
        snap_details = self.replication.get_snapshot_snap_id_details(
            sg_name, snap_name, snap_id)
        i = 0
        if check_unlinked:
            while snap_details.get('linked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to unlink" % i)
                snap_details = self.replication.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        elif check_linked:
            while not snap_details.get('linked'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to link" % i)
                snap_details = self.replication.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        elif check_restored:
            while 'Restored' not in snap_details.get('state'):
                time.sleep(1)
                i += 1
                print("Sleeping for %d seconds while waiting to restore" % i)
                snap_details = self.replication.get_snapshot_snap_id_details(
                    sg_name, snap_name, snap_id)
                if i > 10:
                    break
        return snap_details

    def test_link_gen_snapshot(self):
        """Testot s to cover link snapshot."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.replication.modify_storage_group_snapshot(
            src_storage_grp_id=sg_name, tgt_storage_grp_id=target_sg,
            snap_name=snap_name, gen_num=0, unlink=True)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)
        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_link_snapshot_by_snap_id(self):
        """Test to cover link snapshot by snap id."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.assertIsNotNone(snap_id)
        self.replication.link_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(snap_details.get('linked'))
        self.replication.modify_storage_group_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id, unlink=True)
        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_unlink_gen_snapshot(self):
        """Test to cover unlink snapshot."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        self.replication.link_gen_snapshot(
            sg_id=sg_name, link_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)

        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_linked=True)
        self.assertTrue(snap_details.get('isLinked'))
        self.replication.unlink_gen_snapshot(
            sg_id=sg_name, unlink_sg_name=target_sg, snap_name=snap_name,
            gen_num=0)
        snap_details = self._test_get_ss_gen_detail(
            sg_name, snap_name, gen_num=0, check_unlinked=True)

        self.assertFalse(snap_details.get('isLinked'))
        self.provisioning.delete_storage_group(storage_group_id=target_sg)

    def test_unlink_snapshot_by_snap_id(self):
        """Test to cover unlink snapshot."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        target_sg = "{sg}_lnk".format(sg=sg_name)
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        self.replication.link_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)
        linked_snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_linked=True)
        self.assertTrue(linked_snap_details.get('linked'))
        self.replication.unlink_snapshot_by_snap_id(
            sg_name, target_sg, snap_name, snap_id)

        snap_details = self._test_get_ss_snapid_detail(
            sg_name, snap_name, snap_id, check_unlinked=True)
        self.assertFalse(snap_details.get('linked'))
        self.provisioning.delete_storage_group(target_sg)

    def test_is_volume_in_replication_session(self):
        """Test is_volume_in_replication_session."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        volume = snapshot_info.get('source_volume')
        vol_name = volume[0].get('name')
        snapxv_src = False
        i = 0
        while not snapxv_src:
            time.sleep(1)
            i += 1
            snapxv_tgt, snapxv_src, rdf_group = (
                self.replication.is_volume_in_replication_session(
                    device_id=vol_name))
            if i > 10:
                break
        self.assertTrue(i <= 10)
        self.assertEqual(snapxv_src, True)

    def test_get_snapshot_generation_details(self):
        """Test get_snapshot_generation_details."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_gen_details = self.replication.get_snapshot_generation_details(
            sg_id=sg_name, snap_name=snap_name, gen_num=0)
        self.assertEqual(['Established'], snap_gen_details.get('state'))

    def test_get_snapshot_snap_id_details(self):
        """Test get_snapshot_snap_id_details."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        snap_details = self.replication.get_snapshot_snap_id_details(
            sg_name, snap_name, snap_id)
        self.assertEqual(['Established'], snap_details.get('state'))

    def test_get_storage_group_snapshot_snap_id_list(self):
        """Test get_storage_group_snapshot_snap_id_list."""
        snapshot_info, sg_name = self.create_sg_snapshot()
        snap_name = snapshot_info.get('name')
        snap_id = snapshot_info.get('snapid')
        snap_id_list = (
            self.replication.get_storage_group_snapshot_snap_id_list(
                sg_name, snap_name))
        self.assertEqual([snap_id], snap_id_list)

    def test_get_rdf_group(self):
        """Test get_rdf_group."""
        rdf_group = self.replication.get_rdf_group_list()
        if not rdf_group:
            self.skipTest('test_get_rdf_group - Unable to get an RDF group.')
        rdf_number = rdf_group[0].get('rdfgNumber')
        rdfg_details = self.replication.get_rdf_group(rdf_number=rdf_number)
        self.assertIn('remoteSymmetrix', rdfg_details)

    def test_get_rdf_group_list(self):
        """Test get_rdf_group_list."""
        rdf_number = self.replication.get_rdf_group_list()
        self.assertIsInstance(rdf_number, list)

    def test_get_rdf_group_list_with_parms(self):
        """Test get_rdf_group_list."""
        rdf_number = self.replication.get_rdf_group_list(
            group_type='Dynamic', remote_symmetrix_id=self.conn.remote_array,
            volume_count=0, rdf_mode='Synchronous')
        self.assertIsInstance(rdf_number, list)

    def test_get_rdf_group_volume(self):
        """Test get_rdf_group_volume."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_vol_details = self.replication.get_rdf_group_volume(
            rdf_number=srdf_group_number, device_id=device_id)
        self.assertIn('localRdfGroupNumber', rdf_vol_details)
        self.assertEqual(srdf_group_number,
                         rdf_vol_details.get('localRdfGroupNumber'))

    def test_get_rdf_group_number(self):
        """Test get_rdf_group."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        label = self.replication.get_rdf_group(srdf_group_number).get('label')
        number = self.replication.get_rdf_group_number(label)
        self.assertEqual(srdf_group_number, number)

    def test_get_rdf_group_volume_list(self):
        """Test get_rdf_group_volume_list."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        rdf_volume_list = self.replication.get_rdf_group_volume_list(
            srdf_group_number)
        self.assertIsInstance(rdf_volume_list, list)

    def test_find_expired_snapvx_snapshots(self):
        """Test find_expired_snapvx_snapshots."""
        if self.is_v4:
            self.skipTest('Getting storage group list by generation does '
                          'not work on the V4. Will need logic in this test '
                          'based on uCode.')
        expired_snap_list = self.replication.find_expired_snapvx_snapshots()
        self.assertIsInstance(expired_snap_list, list)

    def test_find_expired_snapvx_snapshots_by_snap_id(self):
        """Test find_expired_snapvx_snapshots_by_snap_ids."""
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots_by_snap_ids())
        self.assertIsInstance(expired_snap_list, list)

    def test_are_volumes_rdf_paired(self):
        """Test are_volumes_rdf_paired."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        pair_state = self.replication.are_volumes_rdf_paired(
            remote_array=self.conn.remote_array, device_id=local_volume,
            target_device=remote_volume, rdf_group=srdf_group_number)
        self.assertIn('Synchronized', pair_state)

    def test_get_storage_group_srdf_group_list(self):
        """Test get_storage_group_srdf_group_list."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdfg_list = self.replication.get_storage_group_srdf_group_list(
            sg_name)
        self.assertIsInstance(sg_rdfg_list, list)

    def test_get_storage_group_srdf_details(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        sg_rdf_details = self.replication.get_storage_group_srdf_details(
            sg_name, srdf_group_number)
        self.assertIsInstance(sg_rdf_details, dict)

    def test_create_storage_group_srdf_pairings(self):
        """Test create_storage_group_srdf_pairings."""
        self.check_for_remote_array()
        sg_name = self.generate_name(object_type='sg')
        vol_name = self.generate_name(object_type='v')
        self.conn.provisioning.create_storage_group(
            self.SRP, sg_name, self.SLO, None, False, 1, 1, 'GB', False, False,
            vol_name)
        self.replication.create_storage_group_srdf_pairings(
            storage_group_id=sg_name, remote_sid=self.conn.remote_array,
            srdf_mode='Synchronous', establish=True, force_new_rdf_group=True)
        srdf_group_number = (
            self.conn.replication.get_storage_group_srdf_group_list(
                sg_name))[0]
        self.addCleanup(self.cleanup_rdfg, sg_name, srdf_group_number)

    # Split Functions Below will have status of Failed over as Source Volume
    # is not masked to a host

    def test_modify_storage_group_srdf(self):
        """Test modify_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.modify_storage_group_srdf(
            sg_name, 'split', srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_suspend_storage_group_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storage_group_srdf(
            sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Suspended', status)

    def test_establish_storage_group_srdf(self):
        """Test establish_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.suspend_storage_group_srdf(sg_name, srdf_group_number)
        self.replication.establish_storage_group_srdf(
            sg_name, srdf_group_number)
        time.sleep(3)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_failover_storage_group_srdf(self):
        """Test get_storage_group_srdf_details."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storage_group_srdf(sg_name,
                                                     srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Failed Over', status)

    def test_failback_storage_group_srdf(self):
        """Test failback_storage_group_srdf."""
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.failover_storage_group_srdf(
            sg_name, srdf_group_number)
        self.replication.failback_storage_group_srdf(
            sg_name, srdf_group_number)
        status = self.replication.get_storage_group_srdf_details(
            storage_group_id=sg_name, rdfg_num=srdf_group_number).get('states')
        self.assertIn('Synchronized', status)

    def test_get_rdf_director_list(self):
        """Test get rdf director list."""
        rdf_director_list = self.replication.get_rdf_director_list()
        self.assertIsInstance(rdf_director_list, list)

    def test_get_rdf_director_detail(self):
        """Test get_rdf_director_detail."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_details = self.replication.get_rdf_director_detail(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_details, dict)
            self.assertIn('directorId', rdf_director_details)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_list(self):
        """Test get_rdf_direector_list."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.replication.get_rdf_director_port_list(
                director_id=rdf_director_list[0])
            self.assertIsInstance(rdf_director_ports, list)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_get_rdf_director_port_details(self):
        """Test get_rdf_director_port_details."""
        rdf_director_list = self.replication.get_rdf_director_list()
        if len(rdf_director_list) > 0:
            rdf_director_ports = self.replication.get_rdf_director_port_list(
                director_id=rdf_director_list[0],
                filters={'rdf_capable': 'true'})
            rdf_port_detail = self.replication.get_rdf_director_port_details(
                director_id=rdf_director_list[0],
                port_id=rdf_director_ports[0])
            self.assertIn('wwn', rdf_port_detail)
        else:
            self.skipTest('Skip get_rdf_director - there are no RDF directors '
                          'configured on the specified array.')

    def test_create_and_delete_rdf_group(self):
        """Test create_rdf_group and delete_rdf_group."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        if not remote_port_list:
            self.skipTest('Skipping test_create_and_delete_rdf_group -'
                          'No remote port list.')

        self.conn.set_array_id(local_array)
        rdf_group = self.get_next_free_srdf_group()
        self.replication.create_rdf_group(
            local_director_port_list=local_port_list,
            remote_array_id=self.conn.remote_array,
            remote_director_port_list=remote_port_list,
            array_id=local_array, local_rdfg_number=rdf_group,
            remote_rdfg_number=rdf_group, label='pyu4v_' + str(rdf_group))
        rdf_group_list = self.replication.get_rdf_group_list()
        rdfg_list = list()
        for group in rdf_group_list:
            rdfg_list.append(group['rdfgNumber'])
        self.assertIn(rdf_group, rdfg_list)
        self.replication.delete_rdf_group(srdf_group_number=rdf_group)
        rdf_group_list = self.replication.get_rdf_group_list()
        rdfg_list = list()
        for group in rdf_group_list:
            rdfg_list.append(group['rdfgNumber'])
        self.assertNotIn(rdf_group, rdfg_list)

    def test_get_rdf_port_remote_connections(self):
        """Test get_rdf_port_remote_connections."""
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        if not remote_port_list:
            self.skipTest('Skipping test_get_rdf_port_remote_connections - '
                          'No remote port list.')
        self.conn.set_array_id(local_array)
        dir_id = local_port_list[0].split(':')[0]
        port_no = local_port_list[0].split(':')[1]
        connections = self.replication.get_rdf_port_remote_connections(
            director_id=dir_id, port_id=port_no)
        self.assertIn('remotePort', connections)

    def test_modify_rdf_group_add_remove_port(self):
        """test adding and removing of port from RDF group."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        if not remote_port_list:
            self.skipTest('Skipping test_modify_rdf_group_add_remove_port - '
                          'no remote port list')
        port_list = list()
        port_list.append(local_port_list[0])
        self.replication.modify_rdf_group(
            action='remove_ports', srdf_group_number=srdf_group,
            port_list=port_list)
        modifed_port_list = self.replication.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertNotIn(local_port_list[0], modifed_port_list)
        self.replication.modify_rdf_group(
            action='add_ports', port_list=port_list,
            srdf_group_number=srdf_group)
        modifed_port_list = self.replication.get_rdf_group(
            rdf_number=srdf_group)['localPorts']
        self.assertIn(local_port_list[0], modifed_port_list)
        self.replication.delete_rdf_group(srdf_group_number=srdf_group)

    def test_modify_rdf_group_change_label(self):
        """Test modify_rdf_group_change_label."""
        srdf_group, local_port_list, remote_port_list = self.setup_srdf_group()
        if not remote_port_list:
            self.skipTest('Skipping test_modify_rdf_group_change_label - '
                          'no remote port list.')
        srdf_group_label = self.generate_name('label')
        self.replication.modify_rdf_group(
            action='set_label', label=srdf_group_label,
            srdf_group_number=srdf_group)
        rdfg_detail = self.replication.get_rdf_group(srdf_group)
        self.assertIn('PyU4V-', rdfg_detail['label'])
        self.replication.delete_rdf_group(srdf_group_number=srdf_group)

    def test_create_storage_group_from_rdfg(self):
        """Test create_storage_group_from_rdfg."""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        storage_group_name = self.generate_name('sg')
        self.replication.create_storage_group_from_rdfg(
            storage_group_name=storage_group_name,
            srdf_group_number=srdf_group_number, rdf_type='RDF1')
        sg_rdfg_list = self.replication.get_storage_group_srdf_group_list(
            storage_group_id=storage_group_name)
        self.assertIn(srdf_group_number, sg_rdfg_list)
        self.provisioning.delete_storage_group(
            storage_group_id=storage_group_name)

    def test_modify_storage_group_srdf_set_consistency_enable(self):
        """Test test_modify_storage_group_srdf to enable consistency."""
        if not self.run_consistency_enable_check():
            self.skipTest(
                'Skip test_modify_storage_group_srdf_set_consistency_enable '
                'This fix is in V9.2.1.7')
        sg_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        self.replication.modify_storage_group_srdf(
            storage_group_id=sg_name, action='setmode',
            srdf_group_number=srdf_group_number,
            options={'setMode': {'mode': 'Asynchronous'}})
        status = self.replication.modify_storage_group_srdf(
            storage_group_id=sg_name, srdf_group_number=srdf_group_number,
            action="EnableConsistency")
        self.assertEqual('Enabled', status.get('consistency_protection'))
        disable_status = self.replication.modify_storage_group_srdf(
            storage_group_id=sg_name, srdf_group_number=srdf_group_number,
            action="DisableConsistency")
        self.assertEqual(
            'Disabled', disable_status.get('consistency_protection'))

    def run_consistency_enable_check(self):
        version, major = self.conn.common.get_uni_version()
        if major == '92':
            version_list = version.split('.')
            if version_list[2] == '1':
                if int(version_list[3]) < 7:
                    return False
        return True

    def test_bulk_terminate_snapshots(self):
        """Test bulk_terminate_snapshots."""
        sg_name = self.create_empty_storage_group()
        self.provisioning.create_volume_from_storage_group_return_id(
            'bulk_terminate_test', sg_name, '1')
        self.replication.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.replication.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.replication.create_storage_group_snapshot(
            sg_name, sg_name, ttl=1, hours=True)
        self.replication.bulk_terminate_snapshots(
            storage_group_id=sg_name, snap_name=sg_name,
            terminate_all_snapshots=True, force=True)
        snapshot_info = self.replication.get_storage_group_snapshot_list(
            sg_name)
        self.assertEquals(0, len(snapshot_info))
