import { useCallback, useEffect, useState } from "react";
import { request } from "../api/http";

export function useResource(path) {
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({
    path: null,
    data: null,
    loading: true,
    error: "",
  });
  const reload = useCallback(() => setRevision((value) => value + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setState({ path, revision, data: null, loading: true, error: "" });
    request(path, { signal: controller.signal }).then(
      (data) => {
        if (active)
          setState({ path, revision, data, loading: false, error: "" });
      },
      (error) => {
        if (active && error.name !== "AbortError")
          setState({
            path,
            revision,
            data: null,
            loading: false,
            error: error.message,
          });
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [path, revision]);
  return {
    ...(state.path === path && state.revision === revision
      ? state
      : { data: null, loading: true, error: "" }),
    reload,
  };
}
