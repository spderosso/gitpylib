"""Module for getting the status of the repo."""


__author__ = "Santiago Perez De Rosso (sperezde@csail.mit.edu)"


import common


SUCCESS = 1
FILE_NOT_FOUND = 2

# Possible status in which a Git file can be in.
TRACKED_UNMODIFIED = 3
TRACKED_MODIFIED = 4
UNTRACKED = 5
ASSUME_UNCHANGED = 6
STAGED = 7


def of_file(fp):
  """Gets the status of the given file.

  Args:
    fp: the path of the file to status (e.g., 'paper.tex').

  Returns:
    FILE_NOT_FOUND if the given file doesn't exist or one of the possible
    status codes (see Status class above).
  """
  ok, out, unused_err = common.git_call(
      'ls-files -tvcdo --error-unmatch %s' % fp)
  if not ok:
    # The file doesn't exist.
    return FILE_NOT_FOUND

  return _status_from_output(out[0], fp)

  
def of_repo():
  """Gets the status of the repo.

  Yields:
      A pair (status, fp) for each file in the repo. fp is a filepath and
      status is the status of the file (TRACKED_UNMODIFIED, TRACKED_MODIFIED,
      UNTRACKED, ASSUME_UNCHANGED or STAGED).
  """
  unused_ok, out, unused_err = common.git_call('ls-files -tvcdo')

  for f_out in out.splitlines():
    # output is 'S filename' where S is a character representing the status of
    # the file.
    fp = f_out[2:]
    yield (_status_from_output(f_out[0], fp), fp)


def _status_from_output(s, fp):
  if s is '?':
    return UNTRACKED
  elif s is 'h':
    return ASSUME_UNCHANGED
  elif s is 'H':
    # We need to use status --porcelain to figure out whether it's modified or
    # not.
    out, unused_err = common.safe_git_call('status --porcelain %s' % fp)
    if len(out) is 0:
      return TRACKED_UNMODIFIED
    s = out.strip()[0] # Output sometimes starts with a space.
    if s is 'M':
      return TRACKED_MODIFIED
    elif s is 'A':
      return STAGED

    raise Exception("Failed to get status of file %s, out %s" % (fp, out))

  raise Exception("Failed to get status of file %s, status %s" % (fp, s))

