import React, { useState } from "react";

function Home() {
  const [players, setPlayers] = useState([]);
  const [draftPicks, setDraftPicks] = useState([]);

  const fetchPlayers = () => {
    fetch("http://localhost:8000/players/")
      .then((res) => res.json())
      .then((data) => setPlayers(data.players))
      .catch((err) => console.error(err));
  };

  const fetchDraftPicks = () => {
    fetch("http://localhost:8000/draft/")
      .then((res) => res.json())
      .then((data) => setDraftPicks(data.draftPicks))
      .catch((err) => console.error(err));
  };

  return (
    <div>
      <div>
        <h1>Players</h1>
        <button onClick={fetchPlayers}>Load Players</button>
        {players.length > 0 && (
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Jersey</th>
                <th>Team ID</th>
                <th>Injury Status</th>
              </tr>
            </thead>
            <tbody>
              {players.map((player) => (
                <tr key={player.id}>
                  <td>{player.fullName}</td>
                  <td>{player.jersey}</td>
                  <td>{player.proTeamId}</td>
                  <td>{player.injuryStatus}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div>
        <h1>Draft Picks</h1>
        <button onClick={fetchDraftPicks}>Load Draft Picks</button>
        {draftPicks.length > 0 && (
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Id</th>
                <th>Keeper?</th>
                <th>Player Id</th>
                <th>Round</th>
                <th>Pick</th>
                <th>Team</th>
                <th>Pick Overall</th>
              </tr>
            </thead>
            <tbody>
              {draftPicks.map((pick) => (
                <tr key={pick.id}>
                  <td>{pick.id}</td>
                  <td>{pick.reservedForKeeper ? "Yes" : "No"}</td>
                  <td>{pick.playerId}</td>
                  <td>{pick.roundId}</td>
                  <td>{pick.roundPickNumber}</td>
                  <td>{pick.teamId}</td>
                  <td>{pick.overallPickNumber}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Home;
