# Sample Payloads

<https://developer.github.com/v3/activity/events/types/>

Types of sample payloads:

* IssueCommentEvent 
* IssuesEvent 
* (LabelEvent)
* (MilestoneEvent)
* (ProjectEvent)
* PullRequestEvent 
* PullRequestReviewEvent 
* PullRequestReviewCommentEvent 
* PushEvent
* ReleaseEvent

## IssueCommentEvent

Issue comment events:

Actions:

* "created"
* "edited"
* "deleted"


## IssuesEvent

Actions:

* "assigned", 
* "unassigned", 
* "labeled", 
* "unlabeled", 
* "opened", 
* "edited", 
* "milestoned", 
* "demilestoned", 
* "closed", 
* "reopened"


## PullRequestEvent

Most complex pull request... lots of possible actions

Actions:
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

* if action is "closed":
	* if "closed" and merge key is false, 
	  PR was closed w/ unmerged commits.
    * if "closed" and merge key is true,
      PR was merged


## PullRequestReviewEvent

action:
* "submitted"
* "edited"
* "dismissed"

The `review` key of the webhook payload
contains info about the review that was
related to this action being triggered.


## PullRequestReviewCommentEvent 

action:
* "created"
* "edited"
* "deleted"

The `pull_request` key of the webhook payload
contains info about the relevant pull request.


## PushEvent

fields:
* ref - the full git ref that was pushed (refs/head/master)
* head - sha of most recent commit after push
* before - sha of most recent commit before push
* size - number of commits
* commits - array describing pushed commits
    * sha
    * message
    * author
    * url 


