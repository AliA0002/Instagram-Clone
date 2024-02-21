import React from "react";
import PropTypes from "prop-types";

class CommentsForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange = () => {
    this.setState({ value: event.target.value });
  };
  handleSubmit = (event) => {
    if (event.keyCode == 13) {
    }
  };

  render() {
    const { like } = this.state;
    return (
      <form onSubmit={this.handleSubmit}>
        {" "}
        <label>
          Name:
          <input
            type="text"
            value={this.state.value}
            onChange={this.handleChange}
            onKeyDown={this.handleSubmit}
          />{" "}
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}
export default CommentsForm;
