/* setup
 *
 * Sets up HDF5 objects for the flusherator.
 */

#include <stdio.h>
#include <stdlib.h>

#include <hdf5.h>

#include "flusherator.h"

int
main(int argc, char *argv[])
{
    hid_t fid     = H5I_INVALID_HID;
    hid_t fapl_id = H5I_INVALID_HID;
    hid_t gid     = H5I_INVALID_HID;
    hid_t sid     = H5I_INVALID_HID;
    hid_t dcpl_id = H5I_INVALID_HID;

    /* Chunk size (ridiculously small size to force MD creation) */
    hsize_t start_dims[1] = {0};
    hsize_t max_dims[1]   = {H5S_UNLIMITED};
    hsize_t chunk_dims[1] = {1};

    printf("flusherator (setup)...\n");

    /* Create fapl to set latest file format */
    if ((fapl_id = H5Pcreate(H5P_FILE_ACCESS)) < 0)
        goto badness;
    if (H5Pset_libver_bounds(fapl_id, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST) < 0)
        goto badness;

    /* Create file and containing group */
    if ((fid = H5Fcreate(FILE_NAME, H5F_ACC_TRUNC, H5P_DEFAULT, fapl_id)) < 0)
        goto badness;
    if ((gid = H5Gcreate2(fid, GROUP_NAME, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT)) < 0)
        goto badness;

    /* Create dataset file space (1D, unlimited) */
    if ((sid = H5Screate_simple(1, start_dims, max_dims)) < 0)
        goto badness;

    /* Create dcpl and set chunking */
    if ((dcpl_id = H5Pcreate(H5P_DATASET_CREATE)) < 0)
        goto badness;
    if (H5Pset_chunk(dcpl_id, 1, chunk_dims) < 0)
        goto badness;

    /* Crate datasets */
    for (int i = 0; i < N_DSETS; i++) {

        hid_t did           = H5I_INVALID_HID;
        char  dset_name[32] = {0};

        snprintf(dset_name, 31, "DSET%d", i);

        if ((did = H5Dcreate2(gid, dset_name, H5T_NATIVE_INT, sid, H5P_DEFAULT, dcpl_id, H5P_DEFAULT)) < 0)
            goto badness;
        if (H5Dclose(did) < 0)
            goto badness;
    }

    /* Close everything */
    if (H5Sclose(sid) < 0)
        goto badness;
    if (H5Pclose(dcpl_id) < 0)
        goto badness;
    if (H5Gclose(gid) < 0)
        goto badness;
    if (H5Pclose(fapl_id) < 0)
        goto badness;
    if (H5Fclose(fid) < 0)
        goto badness;

    printf("DONE\n");

    return EXIT_SUCCESS;

badness:
    printf("BADNESS!!!!!\n");
    return EXIT_FAILURE;
}
