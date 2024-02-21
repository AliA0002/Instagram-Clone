import React from "react";
import PropTypes from "prop-types";
import moment from "moment";
import Comment from "./comment";
import LikesButton from "./LikesButton";

class Post extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: "",
      owner: "",
      ownerImgUrl: "",
      ownerShowUrl: "",
      postShowUrl: "",
      postid: 0,
      url: "",
      commentslist: [],
      comments_url: "",
      timestamp: "",
      likes: [],
      numLikes: 0,
      lognameLikesThis: 0,
      like_string: "",
      likes_post_url: "",
      likes_delete_url: "",
      comments_post_url: "",
      comment_text: "",
    };
  }
  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
          commentslist: data.comments,
          comments_url: data.comments_url,
          timestamp: moment(data.created).fromNow(),
          likes: data.likes,
          numLikes: data.likes.numLikes,
          lognameLikesThis: data.likes.lognameLikesThis ? 1 : 0,
          like_string: data.likes.lognameLikesThis ? "Unlike" : "Like",
          likes_post_url: "/api/v1/likes/?postid=".concat(
            data.postid.toString()
          ),
          likes_delete_url: data.likes.url,
          comments_post_url: "/api/v1/comments/?postid=".concat(
            data.postid.toString()
          ),
        });
        //console.log("DEBUG MODE HAHA")
      })
      .catch((error) => console.log(error));
  }

  handleCommentChange = (event) => {
    this.setState({
      comment_text: event.target.value,
    });
  };

  handleCommentSubmit = (event) => {
    let comments_url = this.state.comments_post_url;
    let comment_text = this.state.comment_text;
    //et self = this;
    if (event.keyCode == 13) {
      // console.log("submit pressed")
      // console.log(comment_text)
      // console.log(comments_url)
      // console.log(typeof comments_url)
      //console.log(typeof JSON.stringify({text:comment_text}))
      fetch(
        comments_url,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          dataType: "json",
          body: JSON.stringify({ text: comment_text }),
        },
        { credentials: "same-origin" }
      )
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            commentslist: prevState.commentslist.concat(data),
            comment_text: "",
          }));
          //console.log(this.state.commentslist)
        })
        .catch((error) => {
          console.log(error);
        });
      event.preventDefault();
    }
  };

  DeleteComment = (id, event) => {
    let delete_url = "/api/v1/comments/".concat(id);
    delete_url = delete_url.concat("/");

    fetch(
      delete_url,
      {
        method: "DELETE",
      },
      { credentials: "same-origin" }
    )
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        this.setState((prevState) => ({
          commentslist: prevState.commentslist.splice(
            prevState.commentslist.findIndex((object) => {
              return object.commentid === id;
            }),
            1
          ),
        }));
      })
      .catch((error) => {
        console.log(error);
      });
    //event.preventDefault();
  };

  handleDoubleClickPost = () => {
    let like = this.state.lognameLikesThis;
    let likes_post_url = this.state.likes_post_url;
    let likes_delete_url = this.state.likes_delete_url;
    let newlikes = this.state.likes;
    if (like == 0) {
      newlikes.numLikes = newlikes.numLikes + 1;
      let new_url = "/api/v1/likes/".concat(newlikes.numLikes.toString());
      new_url = new_url.concat("/");
      newlikes.url = new_url;
      this.setState({
        lognameLikesThis: 1,
        like_string: "Unlike",
        likes: newlikes,
        likes_delete_url: new_url,
      });
      fetch(
        likes_post_url,
        {
          method: "POST",
        },
        { credentials: "same-origin" }
      )
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          console.log(data);
        })
        .catch((error) => console.log(error));
    }
  };

  handleLikeSubmit = () => {
    let like = this.state.lognameLikesThis;
    let likes_post_url = this.state.likes_post_url;
    let likes_delete_url = this.state.likes_delete_url;
    let numLikes = this.state.numLikes;
    //console.log(this.state);
    if (like == 0) {
      // console.log(likes_post_url)
      // console.log(typeof likes_post_url)
      // newlikes.numLikes = newlikes.numLikes + 1
      // let new_url = "/api/v1/likes/".concat(newlikes.numLikes.toString())
      // new_url = new_url.concat("/")
      // newlikes.url = new_url
      fetch(
        likes_post_url,
        {
          method: "POST",
        },
        { credentials: "same-origin" }
      )
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // this.setState({
          //   lognameLikesThis: 1,
          //   like_string: "Unlike",
          //   likes: newlikes,
          //   likes_delete_url: new_url,
          //   });
          this.setState((prevState) => ({
            lognameLikesThis: 1,
            like_string: "Unlike",
            numLikes: prevState.numLikes + 1,
            likes_delete_url: data.url,
          }));
        })
        .catch((error) => console.log(error));
    } else {
      fetch(
        likes_delete_url,
        {
          method: "DELETE",
        },
        { credentials: "same-origin" }
      )
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          // this.setState({
          //   lognameLikesThis: 0,
          //   like_string: "Like",
          //   likes: newlikes,
          //   });
          this.setState((prevState) => ({
            lognameLikesThis: 0,
            like_string: "Like",
            numLikes: prevState.numLikes - 1,
          }));
        })
        .catch((error) => console.log(error));
    }
  };

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl,
      owner,
      ownerImgUrl,
      ownerShowUrl,
      postShowUrl,
      postid,
      commentslist,
      comments_url,
      timestamp,
      likes,
      numLikes,
      likes_post_url,
      likes_delete_url,
      comments_posturl,
    } = this.state;
    // Render post image and post owner

    // let numLikes = likes.numLikes;
    // let userLikes = likes.lognameLikesThis;
    // let likesUrl = likes.url;

    // let postid_str = {postid}
    // postid_str = postid_str.toString();
    // let likes_formurl = "/api/v1/likes/?postid=".concat(postid_str)
    // let comments_posturl = "/api/v1/comments/?postid=".concat(postid_str)

    let comments = [];
    let delete_comments = [];

    commentslist.forEach((comment) => {
      comments.push(
        <Comment
          comment={comment}
          clickHandler={this.DeleteComment}
          key={comment.commentid}
        />
      );
      // if(comment.lognameOwnsThis) {
      //   delete_comments.push(
      //     <button onClick={this.handleDeleteSubmit} id={comment.commentid} className="delete-comment-button">
      //       Delete
      //     </button>

      //   );

      // }
    });
    // commentslist.sort(function(a, b) {
    //     let keyA = a.commentid;
    //     let keyB = b.commentid;
    //     if (keyA > keyB) return 1;
    //     if (keyA < keyB) return -1;
    //     return 0;
    // });

    return (
      <div className="post">
        <div className="poster_image">
          <a href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="image not found."></img>
          </a>
        </div>
        <div className="user_name">
          <a href={ownerShowUrl}>{owner}</a>
        </div>
        <div className="poster_time">
          <a href={postShowUrl}>{timestamp}</a>
        </div>

        <div className="post_image">
          <a href={postShowUrl}>
            <img
              src={imgUrl}
              onDoubleClick={this.handleDoubleClickPost}
              alt="image not found."
            />
          </a>
        </div>

        <div className="post_reply">
          {numLikes == 1 && <p> 1 Like </p>}
          {numLikes != 1 && <p> {numLikes} Likes </p>}

          <div>{comments}</div>

          <button
            onClick={this.handleLikeSubmit}
            className="like-unlike-button"
          >
            {this.state.like_string}
          </button>

          <form
            onKeyDown={this.handleCommentSubmit.bind(this)}
            className="comment-form"
          >
            <input type="hidden" name="operation" value="create" />
            <input type="hidden" name="postid" value={postid} />
            <input
              type="text"
              name="text"
              value={this.state.comment_text}
              onChange={this.handleCommentChange}
              required
            />
            <input type="hidden" name="comment" value="comment" />
          </form>
        </div>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
export default Post;
