-- +goose Up
CREATE TABLE answers (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    answer_text text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- +goose Down
DROP TABLE answers;
