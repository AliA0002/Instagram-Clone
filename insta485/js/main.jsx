import React from "react";
import { createRoot } from "react-dom/client";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";
// Create a root
const root = createRoot(document.getElementById("reactEntry"));
// This method is only called once
// Insert the post component into the DOM
class PostsList extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { postslist: [], pagenum: 0, curr_page_url: "" };
  }

  componentDidMount() {
    const { url } = this.props;

    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          postslist: data.results,
          pagenum: 0,
          curr_page_url: url,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchMoreData = () => {
    let url = this.state.curr_page_url;
    let pagenum = this.state.pagenum;
    let new_url = url;
    if (url.substr(-1) === "/") {
      pagenum = 1;
      new_url = url.concat("?page=");
      new_url = new_url.concat(pagenum.toString());
      console.log("new_page_1");
    } else {
      pagenum = pagenum + 1;
      new_url = "/api/v1/posts/?page=".concat(pagenum.toString());
      console.log("new_page");
    }
    fetch(new_url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (data.results.length == 0) {
          console.log("IS AH EMPTY! ");
        } else {
          this.setState({
            postslist: this.state.postslist.concat(data.results),
            pagenum: pagenum + 1,
            curr_page_url: new_url,
          });
        }
      })
      .catch((error) => console.log(error));
  };
  render() {
    const { postslist } = this.state;
    let posts = [];
    postslist.forEach((post) => {
      posts.push(<Post url={post.url} key={post.postid} />);
    });
    return (
      <InfiniteScroll
        dataLength={10 + this.state.pagenum * 10}
        next={this.fetchMoreData}
        hasMore={true}
        initialScrollY={0}
      >
        <div> {posts} </div>
      </InfiniteScroll>
    );
  }
}

root.render(<PostsList url="/api/v1/posts/" />);
