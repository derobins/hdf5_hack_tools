/* flusherator
 *
 * Excercises the flush code (for testing)
 */

#include <stdio.h>
#include <stdlib.h>

#include <hdf5.h>
#include <hdf5_hl.h>

#include "flusherator.h"

int
main(int argc, char *argv[])
{
    hid_t fid = H5I_INVALID_HID;
    hid_t gid = H5I_INVALID_HID;

    hid_t *dids = NULL;
    int   *buf  = NULL;

    printf("flusherator!\n");

    /* Open the file and containing group. Use SWMR to ensure that flush
     * dependencies, et. al are fully enforced.
     */
    if ((fid = H5Fopen(FILE_NAME, H5F_ACC_RDWR | H5F_ACC_SWMR_WRITE, H5P_DEFAULT)) < 0)
        goto badness;
    if ((gid = H5Gopen2(fid, GROUP_NAME, H5P_DEFAULT)) < 0)
        goto badness;

    /* Allocate array of dataset IDs. These will be held open to put pressure
     * on the metadata cache.
     */
    if (NULL == (dids = malloc(N_DSETS * sizeof(hid_t))))
        goto badness;
    for (int i = 0; i < N_DSETS; i++)
        dids[i] = H5I_INVALID_HID;

    /* Data buffer. Contents are irrelevant. */
    if (NULL == (buf = malloc(N_DATA_POINTS * sizeof(int))))
        goto badness;
    for (int i = 0; i < N_DATA_POINTS; i++)
        buf[i] = i;

    /* Open datasets and write data, generating a lot of dirty metadata in
     * the process (the chunk size is 1 element, so a LOT of index structures
     * will be created).
     */
    for (int i = 0; i < N_DSETS; i++) {

        char  dset_name[32] = {0};

        snprintf(dset_name, 31, "DSET%d", i);

        if ((dids[i] = H5Dopen2(gid, dset_name, H5P_DEFAULT)) < 0)
            goto badness;

        if (H5DOappend(dids[i], H5P_DEFAULT, 0, N_DATA_POINTS, H5T_NATIVE_INT, buf) < 0)
            goto badness;
    }

    /* Flush and refresh the datasets */
    for (int i = 0; i < N_DSETS; i++) {
        if (H5Dflush(dids[i]) < 0)
            goto badness;
        if (H5Drefresh(dids[i]) < 0)
            goto badness;
    }

    /* Close datasets that were purposely held open */
    for (int i = 0; i < N_DSETS; i++) {
        if (H5Dclose(dids[i]) < 0)
            goto badness;
    }

    /* Close everything */
    if (H5Gclose(gid) < 0)
        goto badness;
    if (H5Fclose(fid) < 0)
        goto badness;

    free(dids);
    free(buf);

    printf("DONE\n");

    return EXIT_SUCCESS;

badness:
    printf("BADNESS!!!!!\n");
    return EXIT_FAILURE;
}
