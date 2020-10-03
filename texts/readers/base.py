from tqdm import tqdm


class BaseNewsReader(object):

    # region protected methods

    def _iter_news_info(self, src_folder):
        raise NotImplementedError()

    def _calc_total_approx_news_count(self, src_folder):
        raise NotImplementedError()

    # endregion

    def get_news_iter(self, src_folder, desc=None, start_with_index=0, miniter_count=2000):
        total_files_count = self._calc_total_approx_news_count(src_folder=src_folder)

        it = tqdm(enumerate(self._iter_news_info(src_folder)),
                  desc='Processing Documents {}'.format("" if desc is None else "[{}]".format(desc)),
                  unit='docs',
                  ncols=140,
                  miniters=total_files_count / miniter_count,
                  total=total_files_count)

        for text_index, news_info in it:
            if text_index < start_with_index:
                continue

            yield text_index, news_info
