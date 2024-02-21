import React from "react";
import PropTypes from "prop-types";

class Comment extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      commentid: 0,
      lognameOwnsThis: false,
      owner: "",
      ownerShowUrl: "",
      text: "",
      url: "",
    };
  }
  componentDidMount() {
    // // This line automatically assigns this.props.url to the const variable url
    // const { url } = this.props;
    // // Call REST API to get the post's information
    // fetch(url, { credentials: "same-origin" })
    //   .then((response) => {
    //     if (!response.ok) throw Error(response.statusText);
    //     return response.json();
    //   })
    //   .then((data) => {
    //     this.setState({
    //       commentid: data.commentid,
    //       lognameOwnsThis: data.lognameOwnsThis,
    //       owner: data.owner,
    //       ownerShowUrl: data.ownerShowUrl,
    //       text: data.text,
    //       url: data.url,
    //     });
    //   })
    //   .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { comment } = this.props;
    // Render post image and post owner

    // let numLikes = likes.numLikes;
    // let userLikes = likes.lognameLikesThis;
    // let likesUrl = likes.url;
    return (
      <p>
        <span className="user_name">
          <a href={comment.ownerShowUrl}>{comment.owner}</a>
        </span>
        {comment.text}

        {comment.lognameOwnsThis == 1 && (
          <button
            onClick={() => {
              this.props.clickHandler(comment.commentid);
            }}
            className="delete-comment-button"
          >
            Delete
          </button>
        )}
      </p>
    );
  }
}

Comment.propTypes = {
  comment: PropTypes.object.isRequired,
};
export default Comment;
