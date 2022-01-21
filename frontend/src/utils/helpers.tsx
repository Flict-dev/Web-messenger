import { UserType } from "../components/room/roomTypes";

const getCookie = (name: string): string => {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let c = cookies[i].trim().split("=");
    if (c[0] === name) {
      return c[1];
    }
  }
  return "";
};

const sortUsers = (users: Array<UserType>): Array<UserType> => {
  let sortedUsers = users.sort(function (a, b) {
    if ((a.name < b.name) && !a.online) {
      return -1;
    }
    if ((a.name > b.name) && a.online) {
      return 1;
    }
    return 0;
  });

  return sortedUsers;
};
export { getCookie, sortUsers };
