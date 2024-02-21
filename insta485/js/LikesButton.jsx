import React from "react";
import PropTypes from "prop-types";

class LikesButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { like_string: "", likes_post_url: "", likes_delete_url: "" };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    let like = this.props.like;
    let likes_post_url = this.props.likes_post_url;

    let is_like_unlike = "";
    if (like == 0) {
      is_like_unlike = "Like";
    } else {
      is_like_unlike = "Unlike";
    }
    this.setState({
      like_string: is_like_unlike,
    });
    console.log(like);
  }

  handleChange(event) {
    this.setState({ like_string: event.target.value });
  }
  handleSubmit() {
    const { like, likes_post_url, likes_delete_url } = this.props;
    const { like_string } = this.state;

    if (like == 0) {
      fetch(
        { likes_post_url },
        {
          method: "POST",
        },
        { credentials: "same-origin" }
      )
        .then((response) => response.json())
        .then((result) => {
          console.log("Success:", result);
          //   const event = new Event('Change_like');
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    } else {
      fetch(
        { likes_delete_url },
        {
          method: "DELETE",
        },
        { credentials: "same-origin" }
      )
        .then((response) => response.json())
        .then((result) => {
          console.log("Success:", result);
          //   const event = new Event('Change_like');
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }

  render() {
    return (
      <button onClick={this.handleSubmit} className="like-unlike-button">
        {this.state.like_string}
      </button>
    );
  }
}

LikesButton.propTypes = {
  like: PropTypes.number.isRequired,
  likes_post_url: PropTypes.string.isRequired,
  likes_delete_url: PropTypes.string.isRequired,
};
export default LikesButton;
