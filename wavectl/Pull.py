
from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import json
import time
import datetime
import sys
import tempfile
import shutil
import logging

# External dependencies:
import git

from .BaseCommand import BaseCommand
from .BaseWavefrontCommand import BaseWavefrontCommand
from .Resource import Resource
from .ResourceFactory import ResourceFactory
from .Dashboard import Dashboard
from .GitUtils import GitUtils


class PullError(Exception):
    pass


class PullCommand(BaseWavefrontCommand):
    """ The implementation of the `pull <resource>` command"""

    datetimeFormat = "%Y-%m-%d--%H-%M-%S"

    # TODO: Add the resource name to the pull branch suffix
    pullBranchSuffix = "-pull-branch"

    def maybeSetUserEmail(self, r):
        """If git is not configured correctly for the user, git commands fail
        by saying: "Please tell me who you are." and
        "unable to auto-detect email address".
        In this function we detect if git config has an email address already.
        If not we set some placeholder email address."""

        defaultValue = "ZERO_VALUE_FOR_EMAIL_OPTION"
        reader = r.config_reader()
        if reader.get_value(
            "user",
            "email",
                default=defaultValue) == defaultValue:
            writer = r.config_writer()
            writer.set_value("user", "email", "you@example.com")

    def createNewRepo(self, d):
        """ Create a new git repo and initialize it at the given dir"""
        r = git.Repo.init(d)
        self.maybeSetUserEmail(r)

        # The addition of the README file acts as a first commit and also
        # creates a master branch.
        n = "README.md"
        p = os.path.join(d, n)

        with open(p, "w") as f:
            f.write("This is a repo to manage wavefront resources.")

        r.index.add([p])
        r.index.commit("Initial commit with the README.md file")

        assert(len(r.heads) > 0 and "The initial commit should create a master head")
        assert(r.active_branch.name == "master" and "unexpected active branch")

        # The unix epoch represented in datetime
        minDate = datetime.datetime.fromtimestamp(time.mktime(time.gmtime(0)))
        pbn = minDate.strftime(self.datetimeFormat) + self.pullBranchSuffix
        # Create a pull branch so that future pulls can checkout from
        # thay branch.
        r.heads.master.checkout(b=pbn)

        # Re-checkout the master branch to leave the repo in an reasonable
        # state.
        r.heads.master.checkout()

        return r

    def checkCleanRepo(self, r):
        """ Check that the git repo is "clean". In other words, the repo does
        not contain any staged-but-uncommitted changes and also does not have
        local modifications. """
        if r.is_dirty():
            raise PullError(
                ("The path at {0} is dirty. Please commit your outstanding changes "
                 "and try again... \n{1}").format(
                    r.working_tree_dir, r.git.status()))

    def getNewestPullBranch(self, r):
        """In the given repo there should be several pull branches named like
        <creation-datetime><pullBranchSuffix>. This function returns the newest one
        of those pull branches. If it cannot find any pull branches, it returns
        None"""

        # Get all the pull branches and sort them according to their name

        # compare the names of branches
        def getNameOfBranch(b): return b.name
        pb = sorted([h for h in r.heads if h.name.endswith(
            self.pullBranchSuffix)], key=getNameOfBranch)

        if len(pb) == 0:
            return None
        else:
            b = pb[-1]
            return b

    def saveRsrcs(self, rsrcType, rsrcs, d):
        """Save the given resources of the given resourceType in to the given
        dir. Each resource becomes a separate file with json contents"""
        if len(rsrcs) > 0:
            logging.info("Saving resource files for the ids: {0}".format(
                " ".join([str(r.uniqueId()) + rsrcType.fileExtension()
                          for r in rsrcs])))

        for r in rsrcs:
            id = str(r.uniqueId())
            with open(os.path.join(d, id + rsrcType.fileExtension()), "w") as f:
                f.write(r.jsonStr())
                # TODO: fsync per file? We have seen some automated tests to fail
                # because what looked like some files were not written back to
                # the disk. It would be great to avoid this fsync per file.
                # Could we do this buffer flush once ?
                f.flush()
                os.fsync(f.fileno())

    def purgeDeletedRsrcs(self, rsrcType, d):
        """Get the deleted rsrcs from wavefront. List the resource files in the
        given dir and delete the resource files that also exist in the trashed
        resource list."""
        getF = rsrcType.getDeletedFunction(self.getWavefrontApiClient())
        rawRsrcs = BaseWavefrontCommand.searchAllRsrcsFromWavefront(getF, {})
        deletedRsrcs = [rsrcType.fromDict(r) for r in rawRsrcs]
        deletedIds = [str(r.uniqueId()) for r in deletedRsrcs]

        # Extract the id portion from all files names in the directory.
        # TODO: We may have a new classMethod called fromFile() That reads the
        # file and constructs a Resource. Here we may use that function instead
        # of parsing the file names. That function will be necessary more in
        # the push command impl.
        existingIds = [os.path.splitext(x)[0] for x in os.listdir(d)
                       if x.endswith(rsrcType.fileExtension())]

        # Get the intersection of the deleted resources and the existing
        # resources
        removeIds = list(set(deletedIds) & set(existingIds))

        # Delete resource files for deleted resources.
        if len(removeIds) > 0:
            logging.info(
                ("Some saved resources were deleted. Purging resources with the "
                 "following ids: {0}").format(
                    " ".join([id + rsrcType.fileExtension() for id in removeIds])))

        for id in removeIds:
            os.remove(os.path.join(d, id + rsrcType.fileExtension()))

    def hasStagedFiles(self, repo):
        """Return true if the given repo has staged files"""
        return len(repo.index.diff("HEAD")) > 0

    def commitAndMergeFiles(self, repo, pullBranch, mergeIntoBranch):
        """The repo has some changes to be committed. Commit them to the
        pullBranch (should be current branch) and merge them to the given
        mergeIntoBranch """

        assert(repo.head.ref.name == pullBranch.name
               and "Expected the repo to be at the pullBranch")

        repo.git.commit(
            with_extended_output=True,
            message="Added files due to pull <resource> cmd:{0}".format(
                " ".join(
                    sys.argv)))

        if mergeIntoBranch != self.noBranchName:
            # Merge pull branch into the given branch.

            # checkout the branch given as the merge into branch. We will merge the
            # pulled changes into this branch.
            # TODO: Do some error checking. What if the given merge branch
            # does not exist. For now only the master branch
            # are allowed in the command line. So it should be fine.
            mb = repo.heads[mergeIntoBranch]
            mb.checkout()

            try:
                # with_exdended_output also prints stdout of the git merge
                # error. Apparently git prints the problem resolution to stdout
                # in case of a merge conflict.
                repo.git.merge(pullBranch.name, with_extended_output=True)
            except git.GitCommandError as e:
                print(
                    (
                        "Received a merge error while merging the branch {0} into "
                        "branch {1}. If this is a merge conflict, please go to {2} and "
                        "manually do the merge. Merge command output:\n {3}").format(
                        pullBranch.name,
                        mergeIntoBranch,
                        repo.working_tree_dir,
                        str(e)))
                raise

    def saveRsrcsInRepo(self, rsrcType, rsrcs, d, mergeIntoBranch):
        """ Saves the given resources in the given dir. The resources is a list of
        specialized object representing one wavefront resource.
        """

        if os.path.exists(d):
            r = GitUtils.getExistingRepo(d)
        else:
            BaseCommand.makeDirsIgnoreExisting(d)
            # For a new directory, create a new git repo if the dir is not already
            # in one.
            try:
                r = git.Repo(d, search_parent_directories=True)
            except git.exc.InvalidGitRepositoryError as e:
                r = self.createNewRepo(d)

        self.checkCleanRepo(r)

        # initial branch
        initialB = r.active_branch
        currentB = initialB

        existingPB = self.getNewestPullBranch(r)  # existing pull branch
        if existingPB:
            existingPB.checkout()
            currentB = existingPB

        # Create a new branch
        now = datetime.datetime.now()
        bn = now.strftime(self.datetimeFormat) + self.pullBranchSuffix
        newPB = currentB.checkout(b=bn)

        self.purgeDeletedRsrcs(rsrcType, d)
        self.saveRsrcs(rsrcType, rsrcs, d)

        # Stage everything except untracked files
        r.git.add(update=True)
        # add each existing resource file again to make sure new resources are
        # also added.
        rsrcFiles = BaseWavefrontCommand.getResourceFiles(rsrcType, d)
        r.git.add(rsrcFiles)

        if self.hasStagedFiles(r):
            self.commitAndMergeFiles(r, newPB, mergeIntoBranch)

        initialB.checkout()

    def handleCmd(self, args):
        """ Handles the pull <resource> [...] commands.
        Pulls the given resources from the wavefront api server to a current
        directory"""
        super(PullCommand, self).handleCmd(args)

        rsrcType = args.rsrcType
        rt = ResourceFactory.resourceTypeFromString(rsrcType)
        rsrcs = self.getRsrcsViaWavefrontApiClient(rt, args.customerTag, args)

        d = self._getRealDirPath(args.dir)

        if args.inGit:
            self.saveRsrcsInRepo(rt, rsrcs, d, args.mergeIntoBranch)
        else:
            if not os.path.exists(d):
                BaseCommand.makeDirsIgnoreExisting(d)
            self.purgeDeletedRsrcs(rt, d)
            self.saveRsrcs(rt, rsrcs, d)

    masterBranchName, noBranchName = ("master", "None")

    def _addMergeIntoBranch(self, parser):
        parser.add_argument(
            "--merge-into-branch",
            "-b",
            dest="mergeIntoBranch",
            default=self.masterBranchName,
            choices=[
                self.masterBranchName,
                self.noBranchName],
            help="""The name of the branch to merge into. By default it is the
            {0} branch. If an {1} is passed, no merge is
            processed. The pulled changes remain in the pull branch only. Right
            now only {0} and {1} are supported as parameters""".format(
                self.masterBranchName,
                self.noBranchName))

    def addCmd(self, subParsers):
        """ Adds the necessary command line arguments to the `pull <resource>`
        command using the given subParsers. The `pull` command is used
        to save the existing configs to a local directory in json form.
        Also add a pointer to the function that handles the pull command.
        The function will be called from the __init__ function after parsing the
        arguments.
        """
        p = subParsers.add_parser(
            "pull", help="""pull resrouces from wavefront api server and save them
            in a local directory in json format""")
        p.set_defaults(wavefrontConfigFuncToCall=self.handleCmd)

        self._addMergeIntoBranch(p)
        self._addInGitOption(p)
        p.add_argument(
            "dir",
            help="""Wavefront resource data will be saved in this
            directory""")

        self._addRsrcTypeSubParsers(p)

        super(PullCommand, self).addCmd(p)

    def __init__(self, *args, **kwargs):
        super(PullCommand, self).__init__(*args, **kwargs)
