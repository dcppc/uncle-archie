# Sample Payloads

Types of sample payloads:

* IssueCommentEvent 
* IssuesEvent 
* LabelEvent 
* MilestoneEvent 
* ProjectEvent 
* PullRequestEvent 
* PullRequestReviewEvent 
* PullRequestReviewCommentEvent 
* PushEvent
* ReleaseEvent


## PullRequestEvent

Pull requests:

* Most complex pull request... lots of possible actions

* actions:
	* "assigned"
	* "unassigned"
	* "review_requested"
	* "review_request_removed"
	* "labeled"
	* "unlabeled"
	* "opened"
	* "edited"
	* "closed"
	* "reopened"

* if closed:
	* if "closed" and merge key is false, 
	  PR was closed w/ unmerged commits.
    * if "closed" and merge key is true,
      PR was merged




