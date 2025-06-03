// components/EntryTable.js
import React, { useEffect, useState } from "react";
import axios from "axios";

import {
  MLB_TEAM_IDS,
  FANTASY_TEAM_ABBREVS,
  POSITION_IDS,
} from "../static/constants";

const DataTable = ({ apiUrl }) => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

  useEffect(() => {
    axios
      .get(apiUrl)
      .then((res) => {
        //console.log("response: \n", res.data);
        setPlayers(res.data);
        setLoading(false);
      })
      .catch((err) => {
        // console.error("Error fetching data:", err);
        setLoading(false);
      });
  }, [apiUrl]);

  const formatValue = (key, value) => {
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (key === "pro_team") return MLB_TEAM_IDS[value] ?? "Unknown";
    if (key === "position_id") return POSITION_IDS[value] ?? "Unknown";
    if (key === "fantasy_team_id")
      return FANTASY_TEAM_ABBREVS[value] ?? "Unknown";
    return value;
  };

  const handleSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const sortedPlayers = [...players].sort((a, b) => {
    if (!sortConfig.key) return 0;

    let aValue = a[sortConfig.key];
    let bValue = b[sortConfig.key];

    // Handle null or undefined
    if (aValue === null || aValue === undefined) aValue = "";
    if (bValue === null || bValue === undefined) bValue = "";

    // Handle boolean sorting
    const isBoolean =
      typeof aValue === "boolean" && typeof bValue === "boolean";
    if (isBoolean) {
      if (aValue === bValue) return 0;
      return sortConfig.direction === "asc"
        ? aValue === false
          ? -1
          : 1
        : aValue === true
        ? -1
        : 1;
    }

    // Check if both values are numeric
    const isNumeric =
      !isNaN(parseFloat(aValue)) &&
      !isNaN(parseFloat(bValue)) &&
      typeof aValue !== "boolean" &&
      typeof bValue !== "boolean";

    if (isNumeric) {
      aValue = parseFloat(aValue);
      bValue = parseFloat(bValue);

      if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    } else {
      // Sort as strings, case insensitive
      aValue = aValue.toString().toLowerCase();
      bValue = bValue.toString().toLowerCase();

      if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    }
  });

  if (loading) return <p>Loading table...</p>;
  if (players.length === 0) return <p>No data available.</p>;

  return (
    <table border="1" cellPadding="10">
      <thead>
        <tr>
          {Object.keys(players[0]).map((key) => (
            <th
              key={key}
              onClick={() => handleSort(key)}
              style={{ cursor: "pointer" }}
            >
              {key.toUpperCase()}{" "}
              {sortConfig.key === key
                ? sortConfig.direction === "asc"
                  ? "▲"
                  : "▼"
                : ""}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sortedPlayers.map((entry) => (
          <tr key={entry.id}>
            {Object.entries(entry).map(([key, value], idx) => (
              <td key={idx}>{formatValue(key, value)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DataTable;
