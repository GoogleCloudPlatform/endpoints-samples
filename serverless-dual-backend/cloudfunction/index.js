/**
 * Copyright 2019, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const Datastore = require('@google-cloud/datastore');

const NoteKind = 'note';

// Instantiates a client
const datastore = Datastore();

exports.addNote = (req, res) => {
  const key = datastore.key([NoteKind, new Date().toJSON()]);
  const entity = {
    key: key,
    data: {
      plate: req.query.plate,
      note: req.body.note
    }
  }
  return datastore
    .save(entity)
    .then(() => res.status(200).send(`Note sent.`))
    .catch(err => {
      console.error(err);
      res.status(500).send(err.message);
      return Promise.reject(err);
    });
}
